"""
Document management service for guest document uploads and management
"""
import os
import sqlite3
import datetime
import hashlib
from typing import List, Dict, Any, Optional
from werkzeug.utils import secure_filename
from PIL import Image

class DocumentManager:
    def __init__(self):
        self.db_name = 'multi_hotel.db'
        self.upload_folder = 'static/uploads/documents'
        self.allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx'}
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        
        # Ensure upload directory exists
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def generate_file_hash(self, file_content: bytes) -> str:
        """Generate hash for file content to detect duplicates"""
        return hashlib.md5(file_content).hexdigest()
    
    def check_existing_document(self, document_id: str, document_type: str) -> Optional[Dict]:
        """Check if document already exists in system"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, booking_id, guest_name, file_path, uploaded_at, is_verified
                FROM guest_documents 
                WHERE document_id = ? AND document_type = ?
            ''', (document_id, document_type))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'booking_id': result[1],
                    'guest_name': result[2],
                    'file_path': result[3],
                    'uploaded_at': result[4],
                    'is_verified': result[5]
                }
            return None
        finally:
            conn.close()
    
    def save_document(self, file, booking_id: int, guest_name: str, 
                     document_type: str, document_id: str) -> Dict[str, Any]:
        """Save uploaded document to filesystem and database"""
        if not file or not self.allowed_file(file.filename):
            return {'success': False, 'error': 'Invalid file type'}
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > self.max_file_size:
            return {'success': False, 'error': 'File too large (max 5MB)'}
        
        # Check for existing document
        existing = self.check_existing_document(document_id, document_type)
        if existing:
            return {
                'success': False, 
                'error': 'Document already exists',
                'existing_document': existing
            }
        
        try:
            # Generate secure filename
            filename = secure_filename(file.filename)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = filename.rsplit('.', 1)[1].lower()
            new_filename = f"{booking_id}_{document_type}_{timestamp}.{file_extension}"
            
            # Save file
            file_path = os.path.join(self.upload_folder, new_filename)
            file.save(file_path)
            
            # Optimize image if it's an image file
            if file_extension in ['jpg', 'jpeg', 'png']:
                self._optimize_image(file_path)
            
            # Save to database
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO guest_documents 
                (booking_id, guest_name, document_type, document_id, file_path, file_name, file_size, uploaded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (booking_id, guest_name, document_type, document_id, file_path, filename, file_size, now))
            
            document_db_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'document_id': document_db_id,
                'file_path': file_path,
                'message': 'Document uploaded successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Upload failed: {str(e)}'}
    
    def _optimize_image(self, file_path: str):
        """Optimize image file size while maintaining quality"""
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize if too large
                max_size = (1920, 1080)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save with optimization
                img.save(file_path, optimize=True, quality=85)
        except Exception as e:
            print(f"Image optimization failed: {e}")
    
    def get_booking_documents(self, booking_id: int) -> List[Dict]:
        """Get all documents for a specific booking"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, guest_name, document_type, document_id, file_name, 
                       file_size, uploaded_at, is_verified
                FROM guest_documents 
                WHERE booking_id = ?
                ORDER BY uploaded_at DESC
            ''', (booking_id,))
            
            documents = []
            for row in cursor.fetchall():
                documents.append({
                    'id': row[0],
                    'guest_name': row[1],
                    'document_type': row[2],
                    'document_id': row[3],
                    'file_name': row[4],
                    'file_size': row[5],
                    'uploaded_at': row[6],
                    'is_verified': row[7]
                })
            
            return documents
        finally:
            conn.close()
    
    def search_documents(self, hotel_id: int, search_term: str) -> List[Dict]:
        """Search documents by guest name, document ID, or document type"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT gd.id, gd.booking_id, gd.guest_name, gd.document_type, 
                       gd.document_id, gd.file_name, gd.uploaded_at, gd.is_verified,
                       b.room_id, r.room_number
                FROM guest_documents gd
                JOIN bookings b ON gd.booking_id = b.id
                JOIN rooms r ON b.room_id = r.id
                WHERE b.hotel_id = ? AND (
                    gd.guest_name LIKE ? OR 
                    gd.document_id LIKE ? OR 
                    gd.document_type LIKE ?
                )
                ORDER BY gd.uploaded_at DESC
            ''', (hotel_id, f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            
            documents = []
            for row in cursor.fetchall():
                documents.append({
                    'id': row[0],
                    'booking_id': row[1],
                    'guest_name': row[2],
                    'document_type': row[3],
                    'document_id': row[4],
                    'file_name': row[5],
                    'uploaded_at': row[6],
                    'is_verified': row[7],
                    'room_id': row[8],
                    'room_number': row[9]
                })
            
            return documents
        finally:
            conn.close()
    
    def verify_document(self, document_id: int, verified: bool = True) -> bool:
        """Mark document as verified or unverified"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE guest_documents 
                SET is_verified = ? 
                WHERE id = ?
            ''', (verified, document_id))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error verifying document: {e}")
            return False
        finally:
            conn.close()
    
    def delete_document(self, document_id: int) -> bool:
        """Delete document from database and filesystem"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            # Get file path first
            cursor.execute('SELECT file_path FROM guest_documents WHERE id = ?', (document_id,))
            result = cursor.fetchone()
            
            if not result:
                return False
            
            file_path = result[0]
            
            # Delete from database
            cursor.execute('DELETE FROM guest_documents WHERE id = ?', (document_id,))
            conn.commit()
            
            # Delete file from filesystem
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
        finally:
            conn.close()
    
    def get_hotel_documents_summary(self, hotel_id: int) -> Dict[str, Any]:
        """Get summary of all documents for a hotel"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            # Total documents
            cursor.execute('''
                SELECT COUNT(*) FROM guest_documents gd
                JOIN bookings b ON gd.booking_id = b.id
                WHERE b.hotel_id = ?
            ''', (hotel_id,))
            total_documents = cursor.fetchone()[0]
            
            # Verified documents
            cursor.execute('''
                SELECT COUNT(*) FROM guest_documents gd
                JOIN bookings b ON gd.booking_id = b.id
                WHERE b.hotel_id = ? AND gd.is_verified = 1
            ''', (hotel_id,))
            verified_documents = cursor.fetchone()[0]
            
            # Documents by type
            cursor.execute('''
                SELECT gd.document_type, COUNT(*) FROM guest_documents gd
                JOIN bookings b ON gd.booking_id = b.id
                WHERE b.hotel_id = ?
                GROUP BY gd.document_type
            ''', (hotel_id,))
            documents_by_type = dict(cursor.fetchall())
            
            return {
                'total_documents': total_documents,
                'verified_documents': verified_documents,
                'pending_verification': total_documents - verified_documents,
                'documents_by_type': documents_by_type
            }
        finally:
            conn.close()