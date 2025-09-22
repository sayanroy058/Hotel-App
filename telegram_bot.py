import os
import logging
import sqlite3
import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f'Welcome to the Hotel Management Bot! Your chat ID is: {chat_id}\n'
        f'Please provide this ID to your hotel administrator to receive notifications.'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message when the command /help is issued."""
    help_text = (
        "Available commands:\n"
        "/start - Start the bot and get your chat ID\n"
        "/help - Show this help message\n"
        "/status - Check if your hotel is connected to this bot\n"
    )
    await update.message.reply_text(help_text)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if the chat ID is registered with any hotel."""
    chat_id = str(update.effective_chat.id)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name FROM hotels WHERE telegram_chat_id = ?', (chat_id,))
    hotel = cursor.fetchone()
    conn.close()
    
    if hotel:
        await update.message.reply_text(f'This chat is connected to hotel: {hotel[1]} (ID: {hotel[0]})')
    else:
        await update.message.reply_text(
            'This chat is not connected to any hotel yet. '
            'Please provide your chat ID to the hotel administrator.'
        )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    await update.message.reply_text("I don't understand that command. Type /help for available commands.")

def send_notification(hotel_id, message):
    """Send notification to a specific hotel's Telegram chat."""
    import asyncio
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT telegram_chat_id, telegram_bot_token FROM hotels WHERE id = ? AND telegram_chat_id IS NOT NULL', (hotel_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[0]:
        chat_id = result[0]
        bot_token = result[1] if result[1] else BOT_TOKEN
        try:
            from telegram.ext import Application
            application = Application.builder().token(bot_token).build()
            asyncio.run(application.bot.send_message(chat_id=chat_id, text=message))
            logging.info(f"Notification sent to hotel {hotel_id}, chat {chat_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to send Telegram notification to hotel {hotel_id}: {e}")
            return False
    else:
        logging.warning(f"No chat ID configured for hotel {hotel_id}")
        return False

def main():
    """Start the bot."""
    # Create the Application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()