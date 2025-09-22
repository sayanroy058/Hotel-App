#!/usr/bin/env python3
"""
Hotel Management System - Multi-Hotel Platform
Run this script to start the application
"""

import os
import sys
from multi_hotel_app import app, setup_database

def main():
    print("🏨 Hotel Management System - Multi-Hotel Platform")
    print("=" * 50)
    
    # Setup database
    print("Setting up database...")
    setup_database()
    print("✅ Database setup complete!")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("\n⚠️  Warning: .env file not found!")
        print("Copy .env.example to .env and configure your settings.")
        print("The application will run with default settings for now.")
    
    print("\n🚀 Starting the application...")
    print("📍 Admin Login: admin / admin123")
    print("📍 Access the application at: http://localhost:5000")
    print("\n" + "=" * 50)
    
    # Run the application
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()