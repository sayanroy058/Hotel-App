#!/usr/bin/env python3
"""
Database migration script to add document management features
"""
import sqlite3
import os

DB_NAME = 'multi_hotel.db'

def migrate_database():
    """Add new tables and columns for document management"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Create documents table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS guest_documents (
            id INTEGER PRIMARY KEY,
            booking_id INTEGER NOT NULL,
            guest_name TEXT NOT NULL,
            document_type TEXT NOT NULL,
            document_id TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            file_size INTEGER,
            uploaded_at TEXT NOT NULL,
            is_verified BOOLEAN DEFAULT 0,
            FOREIGN KEY (booking_id) REFERENCES bookings (id),
            UNIQUE(document_id, document_type)
        )
        ''')
        
        # Create uploads directory if it doesn't exist
        uploads_dir = 'static/uploads/documents'
        os.makedirs(uploads_dir, exist_ok=True)
        
        print("✅ Documents table created successfully")
        print("✅ Upload directory created")
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()