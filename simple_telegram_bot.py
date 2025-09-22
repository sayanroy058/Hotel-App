#!/usr/bin/env python3
"""
Simple Telegram Bot for Hotel Management System
Uses direct HTTP requests to avoid library compatibility issues
"""

import os
import json
import sqlite3
import logging
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Database setup
DB_NAME = 'multi_hotel.db'

# Get bot token from environment variable
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8065221659:AAE_nWRSZWtKU09tRacOPvU3xNd80FgXGXE')
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

def send_message(chat_id, text):
    """Send a message to a Telegram chat."""
    url = f'{BASE_URL}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.json()
    except Exception as e:
        logging.error(f"Error sending message: {e}")
        return None

def get_updates(offset=None):
    """Get updates from Telegram."""
    url = f'{BASE_URL}/getUpdates'
    params = {'timeout': 30}
    if offset:
        params['offset'] = offset
    
    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except Exception as e:
        logging.error(f"Error getting updates: {e}")
        return None

def handle_start_command(chat_id):
    """Handle /start command."""
    message = f"""🏨 Welcome to the Hotel Management Bot!

Your chat ID is: <b>{chat_id}</b>

Please provide this ID to your hotel administrator to receive notifications.

Available commands:
/start - Get your chat ID
/help - Show help message
/status - Check hotel connection"""
    
    send_message(chat_id, message)

def handle_help_command(chat_id):
    """Handle /help command."""
    message = """📋 <b>Available Commands:</b>

/start - Start the bot and get your chat ID
/help - Show this help message  
/status - Check if your hotel is connected to this bot

ℹ️ <b>How to use:</b>
1. Send /start to get your chat ID
2. Give your chat ID to your hotel administrator
3. You'll receive booking notifications automatically"""
    
    send_message(chat_id, message)

def handle_status_command(chat_id):
    """Handle /status command."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name FROM hotels WHERE telegram_chat_id = ?', (str(chat_id),))
    hotel = cursor.fetchone()
    conn.close()
    
    if hotel:
        message = f"""✅ <b>Connected!</b>

This chat is connected to:
🏨 <b>{hotel[1]}</b> (ID: {hotel[0]})

You will receive notifications for:
• New bookings
• Check-ins/Check-outs  
• Payment updates
• System alerts"""
    else:
        message = """❌ <b>Not Connected</b>

This chat is not connected to any hotel yet.

To connect:
1. Send /start to get your chat ID
2. Provide the chat ID to your hotel administrator
3. They will configure it in the system"""
    
    send_message(chat_id, message)

def handle_unknown_command(chat_id):
    """Handle unknown commands."""
    message = """❓ I don't understand that command.

Type /help to see available commands."""
    
    send_message(chat_id, message)

def process_update(update):
    """Process a single update."""
    try:
        if 'message' not in update:
            return
        
        message = update['message']
        chat_id = message['chat']['id']
        
        if 'text' not in message:
            return
        
        text = message['text'].strip()
        
        if text == '/start':
            handle_start_command(chat_id)
        elif text == '/help':
            handle_help_command(chat_id)
        elif text == '/status':
            handle_status_command(chat_id)
        elif text.startswith('/'):
            handle_unknown_command(chat_id)
        else:
            handle_unknown_command(chat_id)
            
    except Exception as e:
        logging.error(f"Error processing update: {e}")

def send_notification(hotel_id, message):
    """Send notification to a specific hotel's Telegram chat."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT telegram_chat_id, telegram_bot_token FROM hotels WHERE id = ? AND telegram_chat_id IS NOT NULL', (hotel_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        chat_id = result[0]
        # For now, use the global bot token (can be enhanced later for per-hotel tokens)
        try:
            response = send_message(chat_id, message)
            if response and response.get('ok'):
                logging.info(f"Notification sent to hotel {hotel_id}, chat {chat_id}")
                return True
            else:
                logging.error(f"Failed to send notification: {response}")
                return False
        except Exception as e:
            logging.error(f"Failed to send Telegram notification to hotel {hotel_id}: {e}")
            return False
    else:
        logging.warning(f"No chat ID configured for hotel {hotel_id}")
        return False

def main():
    """Start the bot."""
    print(f"Starting Simple Telegram Bot...")
    print(f"Bot Token: {BOT_TOKEN[:10]}...")
    print("Bot is running. Press Ctrl+C to stop.")
    
    offset = None
    
    try:
        while True:
            updates_response = get_updates(offset)
            
            if not updates_response or not updates_response.get('ok'):
                time.sleep(1)
                continue
            
            updates = updates_response.get('result', [])
            
            for update in updates:
                process_update(update)
                offset = update['update_id'] + 1
            
            if not updates:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        logging.error(f"Error running bot: {e}")
        print(f"Error running bot: {e}")

if __name__ == '__main__':
    main()