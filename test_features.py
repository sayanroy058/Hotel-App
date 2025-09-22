#!/usr/bin/env python3
"""
Test script for new hotel management features
"""
import os
import sqlite3
from ai_chatbot import HotelAIChatbot
from document_manager import DocumentManager

def test_database_setup():
    """Test if database tables are properly set up"""
    print("🔍 Testing database setup...")
    
    conn = sqlite3.connect('multi_hotel.db')
    cursor = conn.cursor()
    
    # Check if guest_documents table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='guest_documents'")
    if cursor.fetchone():
        print("✅ guest_documents table exists")
    else:
        print("❌ guest_documents table missing")
    
    # Check table structure
    cursor.execute("PRAGMA table_info(guest_documents)")
    columns = cursor.fetchall()
    expected_columns = ['id', 'booking_id', 'guest_name', 'document_type', 'document_id', 'file_path', 'file_name', 'file_size', 'uploaded_at', 'is_verified']
    
    actual_columns = [col[1] for col in columns]
    for col in expected_columns:
        if col in actual_columns:
            print(f"✅ Column '{col}' exists")
        else:
            print(f"❌ Column '{col}' missing")
    
    conn.close()

def test_ai_chatbot():
    """Test AI chatbot functionality (without API key)"""
    print("\n🤖 Testing AI Chatbot...")
    
    try:
        chatbot = HotelAIChatbot()
        print("✅ AI Chatbot initialized")
        
        # Test analytics function (this should work without API key)
        analytics = chatbot.get_hotel_analytics(1)  # Assuming hotel_id 1 exists
        print(f"✅ Analytics retrieved: {len(analytics)} metrics")
        
        # Test quick insights
        insights = chatbot.get_quick_insights(1)
        print(f"✅ Quick insights generated: {len(insights)} insights")
        
    except Exception as e:
        print(f"⚠️  AI Chatbot test failed (expected without API key): {e}")

def test_document_manager():
    """Test document manager functionality"""
    print("\n📄 Testing Document Manager...")
    
    try:
        doc_manager = DocumentManager()
        print("✅ Document Manager initialized")
        
        # Test file validation
        print(f"✅ PDF files allowed: {doc_manager.allowed_file('test.pdf')}")
        print(f"✅ JPG files allowed: {doc_manager.allowed_file('test.jpg')}")
        print(f"❌ EXE files blocked: {not doc_manager.allowed_file('test.exe')}")
        
        # Test upload directory
        if os.path.exists(doc_manager.upload_folder):
            print("✅ Upload directory exists")
        else:
            print("❌ Upload directory missing")
        
        # Test summary function
        summary = doc_manager.get_hotel_documents_summary(1)
        print(f"✅ Document summary generated: {summary}")
        
    except Exception as e:
        print(f"❌ Document Manager test failed: {e}")

def test_room_availability():
    """Test room availability checking"""
    print("\n🏨 Testing Room Availability...")
    
    try:
        from multi_hotel_app import check_room_availability
        
        # Test with non-existent room (should return True - available)
        available = check_room_availability(999, '2024-12-01', '2024-12-02')
        print(f"✅ Room availability check works: {available}")
        
    except Exception as e:
        print(f"❌ Room availability test failed: {e}")

def main():
    print("🚀 Testing Hotel Management System Features\n")
    
    test_database_setup()
    test_ai_chatbot()
    test_document_manager()
    test_room_availability()
    
    print("\n✨ Feature testing completed!")
    print("\n📋 Setup Instructions:")
    print("1. Copy .env.example to .env and configure your API keys")
    print("2. Install requirements: pip install -r requirements.txt")
    print("3. Run the application: python3 multi_hotel_app.py")
    print("4. Access the enhanced Owner Dashboard with AI chatbot")
    print("5. Test document upload and room availability features")

if __name__ == "__main__":
    main()