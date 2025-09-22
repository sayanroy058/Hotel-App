#!/usr/bin/env python3
"""
Telegram Bot Runner for Hotel Management System
Run this script separately to start the Telegram bot
"""

import simple_telegram_bot as telegram_bot

if __name__ == '__main__':
    print("Starting Hotel Management Telegram Bot...")
    print("Bot Token:", telegram_bot.BOT_TOKEN[:10] + "..." if telegram_bot.BOT_TOKEN else "Not configured")
    print("Press Ctrl+C to stop the bot")
    
    try:
        telegram_bot.main()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error running bot: {e}")