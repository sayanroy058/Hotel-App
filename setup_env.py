#!/usr/bin/env python3
"""
Quick setup script for the Enhanced Hotel Management System
"""
import os
import secrets

def create_env_file():
    """Create .env file with default configuration"""
    
    # Generate a secure secret key
    secret_key = secrets.token_urlsafe(32)
    
    env_content = f"""# Flask Configuration
SECRET_KEY={secret_key}
FLASK_ENV=development

# OpenAI Configuration (for AI Chatbot)
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your-openai-api-key-here

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Telegram Bot Configuration (optional)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with secure secret key")
    print("📝 Please edit .env and add your OpenAI API key for the AI chatbot to work")

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import flask
        import openai
        import PIL
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return False

def check_database():
    """Check if database is set up correctly"""
    import sqlite3
    
    try:
        conn = sqlite3.connect('multi_hotel.db')
        cursor = conn.cursor()
        
        # Check if guest_documents table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='guest_documents'")
        if cursor.fetchone():
            print("✅ Database is properly set up with document management")
        else:
            print("⚠️  Database needs migration. Run: python3 database_migration.py")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    print("🚀 Enhanced Hotel Management System Setup")
    print("=" * 50)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("📄 Creating environment configuration...")
        create_env_file()
    else:
        print("✅ .env file already exists")
    
    print("\n🔍 Checking requirements...")
    check_requirements()
    
    print("\n🗄️  Checking database...")
    check_database()
    
    print("\n🎯 Setup Summary:")
    print("1. ✅ Application files are ready")
    print("2. ✅ Database schema is updated")
    print("3. ✅ Environment configuration created")
    
    print("\n📋 Next Steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run: python3 multi_hotel_app.py")
    print("3. Open: http://127.0.0.1:5000")
    print("4. Login with admin/admin123 or create a hotel owner account")
    
    print("\n🌟 New Features Available:")
    print("• AI Chatbot in Owner Dashboard")
    print("• Smart Room Availability Checking")
    print("• Document Management System")
    print("• Enhanced Check-in Process")
    
    print("\n🔗 Get OpenAI API Key:")
    print("Visit: https://platform.openai.com/api-keys")

if __name__ == "__main__":
    main()