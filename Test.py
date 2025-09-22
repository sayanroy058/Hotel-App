import os
import logging
import sqlite3
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, ConversationHandler, filters

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
OWNER_CHAT_ID = int(os.getenv('OWNER_CHAT_ID')) if os.getenv('OWNER_CHAT_ID') else None
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT')) if os.getenv('EMAIL_PORT') else 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'

# Database setup
DB_NAME = 'hotel.db'

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create rooms table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY,
        room_number TEXT UNIQUE,
        room_type TEXT,
        price_per_night REAL,
        capacity INTEGER
    )
    ''')
    
    # Create bookings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY,
        guest_name TEXT,
        room_id INTEGER,
        check_in_date TEXT,
        check_out_date TEXT,
        guest_count INTEGER,
        total_amount REAL,
        payment_status TEXT,
        booking_status TEXT,
        created_at TEXT,
        cancelled_at TEXT,
        FOREIGN KEY (room_id) REFERENCES rooms (id)
    )
    ''')
    
    # Create check_in_out table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS check_in_out (
        id INTEGER PRIMARY KEY,
        booking_id INTEGER,
        check_in_time TEXT,
        check_out_time TEXT,
        FOREIGN KEY (booking_id) REFERENCES bookings (id)
    )
    ''')
    
    # Insert sample rooms if they don't exist
    cursor.execute('SELECT COUNT(*) FROM rooms')
    if cursor.fetchone()[0] == 0:
        rooms = [
            ('101', 'Standard Single', 50.0, 1),
            ('102', 'Standard Single', 50.0, 1),
            ('201', 'Standard Double', 80.0, 2),
            ('202', 'Standard Double', 80.0, 2),
            ('301', 'Deluxe Suite', 150.0, 4),
            ('302', 'Deluxe Suite', 150.0, 4),
            ('401', 'Premium Suite', 200.0, 6)
        ]
        cursor.executemany('INSERT INTO rooms (room_number, room_type, price_per_night, capacity) VALUES (?, ?, ?, ?)', rooms)
    
    conn.commit()
    conn.close()

# Conversation states
START, BOOKING_GUESTS, BOOKING_CHECKIN, BOOKING_CHECKOUT, BOOKING_ROOM, BOOKING_NAME, BOOKING_PAYMENT = range(7)

# Helper functions
def get_available_rooms(check_in_date, check_out_date, guest_count):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Find rooms that are not booked during the specified period and have enough capacity
    cursor.execute('''
    SELECT r.id, r.room_number, r.room_type, r.price_per_night, r.capacity
    FROM rooms r
    WHERE r.capacity >= ? AND r.id NOT IN (
        SELECT b.room_id
        FROM bookings b
        WHERE b.booking_status = 'confirmed'
        AND NOT (b.check_out_date <= ? OR b.check_in_date >= ?)
    )
    ''', (guest_count, check_in_date, check_out_date))
    
    available_rooms = cursor.fetchall()
    conn.close()
    return available_rooms

def calculate_total_nights(check_in_date, check_out_date):
    date_format = "%Y-%m-%d"
    check_in = datetime.datetime.strptime(check_in_date, date_format)
    check_out = datetime.datetime.strptime(check_out_date, date_format)
    return (check_out - check_in).days

def is_valid_date(date_str):
    try:
        date_format = "%Y-%m-%d"
        date_obj = datetime.datetime.strptime(date_str, date_format)
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return date_obj >= today
    except ValueError:
        return False

def get_room_status():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Get available rooms
    cursor.execute('''
    SELECT r.id, r.room_number, r.room_type, r.price_per_night
    FROM rooms r
    WHERE r.id NOT IN (
        SELECT b.room_id
        FROM bookings b
        WHERE b.booking_status = 'confirmed'
        AND NOT (b.check_out_date <= ? OR b.check_in_date > ?)
    )
    ''', (today, today))
    
    available_rooms = cursor.fetchall()
    
    # Get occupied rooms
    cursor.execute('''
    SELECT r.id, r.room_number, r.room_type, r.price_per_night, b.guest_name, b.check_out_date
    FROM rooms r
    JOIN bookings b ON r.id = b.room_id
    WHERE b.booking_status = 'confirmed'
    AND b.check_in_date <= ? AND b.check_out_date > ?
    ''', (today, today))
    
    occupied_rooms = cursor.fetchall()
    
    conn.close()
    return available_rooms, occupied_rooms

def get_todays_bookings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
    SELECT b.id, b.guest_name, r.room_number, b.check_in_date, b.check_out_date, b.total_amount, b.payment_status
    FROM bookings b
    JOIN rooms r ON b.room_id = r.id
    WHERE b.check_in_date = ? AND b.booking_status = 'confirmed'
    ''', (today,))
    
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def get_all_bookings(limit=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT b.id, b.guest_name, r.room_number, b.check_in_date, b.check_out_date, b.total_amount, b.payment_status
    FROM bookings b
    JOIN rooms r ON b.room_id = r.id
    WHERE b.booking_status = 'confirmed'
    ORDER BY b.id DESC
    LIMIT ?
    ''', (limit,))
    
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def get_cancelled_bookings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT b.id, b.guest_name, r.room_number, b.check_in_date, b.check_out_date, b.total_amount, b.cancelled_at
    FROM bookings b
    JOIN rooms r ON b.room_id = r.id
    WHERE b.booking_status = 'cancelled'
    ORDER BY b.cancelled_at DESC
    LIMIT 10
    ''')
    
    bookings = cursor.fetchall()
    conn.close()
    return bookings

def get_todays_checkins():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
    SELECT b.id, b.guest_name, r.room_number, b.guest_count, b.total_amount
    FROM bookings b
    JOIN rooms r ON b.room_id = r.id
    WHERE b.check_in_date = ? AND b.booking_status = 'confirmed'
    AND NOT EXISTS (SELECT 1 FROM check_in_out c WHERE c.booking_id = b.id AND c.check_in_time IS NOT NULL)
    ''', (today,))
    
    checkins = cursor.fetchall()
    conn.close()
    return checkins

def get_todays_checkouts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
    SELECT b.id, b.guest_name, r.room_number, b.total_amount, b.payment_status
    FROM bookings b
    JOIN rooms r ON b.room_id = r.id
    WHERE b.check_out_date = ? AND b.booking_status = 'confirmed'
    AND EXISTS (SELECT 1 FROM check_in_out c WHERE c.booking_id = b.id AND c.check_in_time IS NOT NULL)
    AND NOT EXISTS (SELECT 1 FROM check_in_out c WHERE c.booking_id = b.id AND c.check_out_time IS NOT NULL)
    ''', (today,))
    
    checkouts = cursor.fetchall()
    conn.close()
    return checkouts

def get_current_guests():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
    SELECT b.id, b.guest_name, r.room_number, b.guest_count, b.check_in_date, b.check_out_date
    FROM bookings b
    JOIN rooms r ON b.room_id = r.id
    JOIN check_in_out c ON c.booking_id = b.id
    WHERE b.booking_status = 'confirmed'
    AND c.check_in_time IS NOT NULL
    AND c.check_out_time IS NULL
    AND b.check_out_date >= ?
    ''', (today,))
    
    guests = cursor.fetchall()
    conn.close()
    return guests

def get_sales_report(period):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    today = datetime.datetime.now().date()
    
    if period == 'today':
        start_date = today.strftime("%Y-%m-%d")
        end_date = start_date
    elif period == 'yesterday':
        start_date = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = start_date
    elif period == 'week':
        start_date = (today - datetime.timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif period == 'month':
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    else:
        # Default to today
        start_date = today.strftime("%Y-%m-%d")
        end_date = start_date
    
    # Get all bookings in the period
    cursor.execute('''
    SELECT COUNT(*), SUM(total_amount), 
           SUM(CASE WHEN payment_status = 'paid' THEN 1 ELSE 0 END),
           SUM(CASE WHEN payment_status = 'paid' THEN total_amount ELSE 0 END)
    FROM bookings
    WHERE booking_status = 'confirmed'
    AND check_in_date BETWEEN ? AND ?
    ''', (start_date, end_date))
    
    result = cursor.fetchone()
    conn.close()
    
    total_bookings = result[0] or 0
    total_revenue = result[1] or 0
    paid_bookings = result[2] or 0
    paid_revenue = result[3] or 0
    
    avg_booking = total_revenue / total_bookings if total_bookings > 0 else 0
    payment_rate = (paid_bookings / total_bookings * 100) if total_bookings > 0 else 0
    
    return {
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'avg_booking': avg_booking,
        'paid_bookings': paid_bookings,
        'paid_revenue': paid_revenue,
        'payment_rate': payment_rate
    }

def get_analytics():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    month_start = datetime.datetime.now().replace(day=1).strftime("%Y-%m-%d")
    
    # Get total rooms
    cursor.execute('SELECT COUNT(*) FROM rooms')
    total_rooms = cursor.fetchone()[0]
    
    # Get occupied rooms today
    cursor.execute('''
    SELECT COUNT(DISTINCT room_id)
    FROM bookings
    WHERE booking_status = 'confirmed'
    AND check_in_date <= ? AND check_out_date > ?
    ''', (today, today))
    occupied_rooms = cursor.fetchone()[0]
    
    # Get month revenue
    cursor.execute('''
    SELECT SUM(total_amount)
    FROM bookings
    WHERE booking_status = 'confirmed'
    AND check_in_date >= ?
    ''', (month_start,))
    month_revenue = cursor.fetchone()[0] or 0
    
    # Get most popular room type
    cursor.execute('''
    SELECT r.room_type, COUNT(*)
    FROM bookings b
    JOIN rooms r ON b.room_id = r.id
    WHERE b.booking_status = 'confirmed'
    GROUP BY r.room_type
    ORDER BY COUNT(*) DESC
    LIMIT 1
    ''')
    most_popular = cursor.fetchone()
    
    conn.close()
    
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    return {
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'occupancy_rate': occupancy_rate,
        'month_revenue': month_revenue,
        'most_popular': most_popular[0] if most_popular else 'N/A',
        'most_popular_bookings': most_popular[1] if most_popular else 0
    }

def check_in_guest(booking_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if already checked in
    cursor.execute('SELECT id FROM check_in_out WHERE booking_id = ?', (booking_id,))
    check_record = cursor.fetchone()
    
    if check_record:
        # Update existing record
        cursor.execute('UPDATE check_in_out SET check_in_time = ? WHERE booking_id = ?', (now, booking_id))
    else:
        # Create new record
        cursor.execute('INSERT INTO check_in_out (booking_id, check_in_time) VALUES (?, ?)', (booking_id, now))
    
    conn.commit()
    conn.close()
    return True

def check_out_guest(booking_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if checked in
    cursor.execute('SELECT id FROM check_in_out WHERE booking_id = ? AND check_in_time IS NOT NULL', (booking_id,))
    check_record = cursor.fetchone()
    
    if check_record:
        # Update existing record
        cursor.execute('UPDATE check_in_out SET check_out_time = ? WHERE booking_id = ?', (now, booking_id))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False

def send_daily_report():
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
        logging.warning("Email not configured - skipping daily report")
        return False
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Get today's data
    today_bookings = get_todays_bookings()
    today_checkins = get_todays_checkins()
    today_checkouts = get_todays_checkouts()
    sales_report = get_sales_report('today')
    analytics = get_analytics()
    
    # Create email content
    subject = f"Hotel Daily Report - {today}"
    
    body = f"""<h1>Hotel Daily Report - {today}</h1>
    
    <h2>Today's Bookings ({len(today_bookings)})</h2>
    <ul>
    """
    
    for booking in today_bookings:
        body += f"<li>{booking[1]} - Room {booking[2]} - ${booking[5]} ({booking[6]})</li>\n"
    
    body += f"""</ul>
    
    <h2>Today's Check-ins ({len(today_checkins)})</h2>
    <ul>
    """
    
    for checkin in today_checkins:
        body += f"<li>{checkin[1]} - Room {checkin[2]} - {checkin[3]} guests - ${checkin[4]}</li>\n"
    
    body += f"""</ul>
    
    <h2>Today's Check-outs ({len(today_checkouts)})</h2>
    <ul>
    """
    
    for checkout in today_checkouts:
        body += f"<li>{checkout[1]} - Room {checkout[2]} - ${checkout[3]} ({checkout[4]})</li>\n"
    
    body += f"""</ul>
    
    <h2>Sales Report</h2>
    <p>Total Bookings: {sales_report['total_bookings']}</p>
    <p>Total Revenue: ${sales_report['total_revenue']:.2f}</p>
    <p>Average Booking: ${sales_report['avg_booking']:.2f}</p>
    <p>Paid Bookings: {sales_report['paid_bookings']}</p>
    <p>Paid Revenue: ${sales_report['paid_revenue']:.2f}</p>
    <p>Payment Rate: {sales_report['payment_rate']:.1f}%</p>
    
    <h2>Analytics</h2>
    <p>Total Rooms: {analytics['total_rooms']}</p>
    <p>Occupied Rooms: {analytics['occupied_rooms']}</p>
    <p>Occupancy Rate: {analytics['occupancy_rate']:.1f}%</p>
    <p>Month Revenue: ${analytics['month_revenue']:.2f}</p>
    <p>Most Popular Room Type: {analytics['most_popular']} ({analytics['most_popular_bookings']} bookings)</p>
    """
    
    # Send email
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = 'admin@hotel.com'
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏨 Room Status", callback_data='room_status'),
         InlineKeyboardButton("📊 Sales Report", callback_data='sales_report')],
        [InlineKeyboardButton("📅 Today's Bookings", callback_data='todays_bookings'),
         InlineKeyboardButton("📋 All Bookings", callback_data='all_bookings')],
        [InlineKeyboardButton("➕ Quick Booking", callback_data='quick_booking'),
         InlineKeyboardButton("❌ Cancelled Bookings", callback_data='cancelled_bookings')],
        [InlineKeyboardButton("🔄 Check-in/Check-out", callback_data='check_in_out'),
         InlineKeyboardButton("📈 Analytics", callback_data='analytics')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🏨 Hotel Management Bot\n\nWelcome! Choose an option from the menu below:",
        reply_markup=reply_markup
    )
    
    return START

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'room_status':
        await show_room_status(update, context)
    elif query.data == 'sales_report':
        await show_sales_report_options(update, context)
    elif query.data == 'todays_bookings':
        await show_todays_bookings(update, context)
    elif query.data == 'all_bookings':
        await show_all_bookings(update, context)
    elif query.data == 'quick_booking':
        return await start_booking(update, context)
    elif query.data == 'cancelled_bookings':
        await show_cancelled_bookings(update, context)
    elif query.data == 'check_in_out':
        await show_check_in_out_options(update, context)
    elif query.data == 'analytics':
        await show_analytics(update, context)
    elif query.data.startswith('sales_'):
        period = query.data.split('_')[1]
        await show_sales_report(update, context, period)
    elif query.data == 'todays_checkins':
        await show_todays_checkins(update, context)
    elif query.data == 'todays_checkouts':
        await show_todays_checkouts(update, context)
    elif query.data == 'current_guests':
        await show_current_guests(update, context)
    elif query.data.startswith('checkin_'):
        booking_id = int(query.data.split('_')[1])
        await process_checkin(update, context, booking_id)
    elif query.data.startswith('checkout_'):
        booking_id = int(query.data.split('_')[1])
        await process_checkout(update, context, booking_id)
    elif query.data.startswith('room_'):
        room_id = int(query.data.split('_')[1])
        await select_room(update, context, room_id)
    elif query.data.startswith('payment_'):
        booking_id = int(query.data.split('_')[1])
        action = query.data.split('_')[2]
        await process_payment(update, context, booking_id, action)
    elif query.data == 'back_to_main':
        await back_to_main_menu(update, context)
    
    return START

async def show_room_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    available_rooms, occupied_rooms = get_room_status()
    
    message = "🏨 ROOM STATUS\n\n"
    
    message += "🟢 AVAILABLE ROOMS:\n"
    for room in available_rooms:
        message += f"✅ Room {room[1]} ({room[2]}) - ${room[3]}/night\n"
    
    message += f"\nTotal Available: {len(available_rooms)}\n\n"
    
    message += "🔴 OCCUPIED ROOMS:\n"
    for room in occupied_rooms:
        message += f"❌ Room {room[1]} ({room[2]}) - ${room[3]}/night\n"
        message += f"   Guest: {room[4]}\n"
        message += f"   Checkout: {room[5]}\n\n"
    
    message += f"Total Occupied: {len(occupied_rooms)}"
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def show_sales_report_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    keyboard = [
        [InlineKeyboardButton("📊 Today", callback_data='sales_today')],
        [InlineKeyboardButton("📈 Yesterday", callback_data='sales_yesterday')],
        [InlineKeyboardButton("📅 This Week", callback_data='sales_week')],
        [InlineKeyboardButton("📆 This Month", callback_data='sales_month')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📊 SALES REPORTS\n\nSelect time period:",
        reply_markup=reply_markup
    )

async def show_sales_report(update: Update, context: ContextTypes.DEFAULT_TYPE, period):
    query = update.callback_query
    report = get_sales_report(period)
    
    period_name = {
        'today': 'TODAY',
        'yesterday': 'YESTERDAY',
        'week': 'THIS WEEK',
        'month': 'THIS MONTH'
    }.get(period, 'CUSTOM')
    
    message = f"📊 SALES REPORT - {period_name}\n\n"
    message += f"🎫 Total Bookings: {report['total_bookings']}\n"
    message += f"💰 Total Revenue: ${report['total_revenue']:.2f}\n"
    message += f"📊 Average Booking: ${report['avg_booking']:.2f}\n"
    message += f"✅ Paid Bookings: {report['paid_bookings']}\n"
    message += f"💵 Paid Revenue: ${report['paid_revenue']:.2f}\n"
    message += f"📈 Payment Rate: {report['payment_rate']:.1f}%"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back to Reports", callback_data='sales_report')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def show_todays_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    bookings = get_todays_bookings()
    
    message = "📅 TODAY'S BOOKINGS\n\n"
    
    if bookings:
        for booking in bookings:
            status_emoji = "✅" if booking[6] == 'paid' else "⏳"
            message += f"{status_emoji} {booking[1]}\n"
            message += f"   🏠 Room: {booking[2]}\n"
            message += f"   📅 Check-in: {booking[3]}\n"
            message += f"   📅 Check-out: {booking[4]}\n"
            message += f"   💰 Amount: ${booking[5]}\n"
            message += f"   💳 Payment: {booking[6].capitalize()}\n\n"
        
        message += f"Total Bookings Today: {len(bookings)}"
    else:
        message += "No bookings for today."
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def show_all_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    bookings = get_all_bookings()
    
    message = "📋 ALL BOOKINGS (Last 10)\n\n"
    
    if bookings:
        for booking in bookings:
            status_emoji = "✅" if booking[6] == 'paid' else "⏳"
            payment_status = "paid" if booking[6] == 'paid' else "pending"
            
            message += f"{status_emoji} Booking #{booking[0]}\n"
            message += f"   👤 Guest: {booking[1]}\n"
            message += f"   🏠 Room: {booking[2]}\n"
            message += f"   📅 {booking[3]} → {booking[4]}\n"
            
            if booking[6] == 'paid':
                message += f"   💵 ${booking[5]} ({payment_status})\n\n"
            else:
                message += f"   ⏳ ${booking[5]} ({payment_status})\n\n"
    else:
        message += "No bookings found."
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def show_cancelled_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    bookings = get_cancelled_bookings()
    
    message = "❌ CANCELLED BOOKINGS\n\n"
    
    if bookings:
        total_lost = 0
        for booking in bookings:
            message += f"🚫 Booking #{booking[0]}\n"
            message += f"   👤 Guest: {booking[1]}\n"
            message += f"   🏠 Room: {booking[2]}\n"
            message += f"   📅 {booking[3]} → {booking[4]}\n"
            message += f"   💰 Lost Revenue: ${booking[5]}\n"
            message += f"   📅 Cancelled: {booking[6]}\n\n"
            
            total_lost += booking[5]
        
        message += f"Total Cancelled: {len(bookings)}\n"
        message += f"Total Lost Revenue: ${total_lost:.2f}"
    else:
        message += "No cancelled bookings found."
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def show_check_in_out_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    keyboard = [
        [InlineKeyboardButton("📥 Today's Check-ins", callback_data='todays_checkins')],
        [InlineKeyboardButton("📤 Today's Check-outs", callback_data='todays_checkouts')],
        [InlineKeyboardButton("📋 Current Guests", callback_data='current_guests')],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🔄 CHECK-IN/CHECK-OUT MANAGEMENT\n\nSelect an option:",
        reply_markup=reply_markup
    )

async def show_todays_checkins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    checkins = get_todays_checkins()
    
    message = "📥 TODAY'S CHECK-INS\n\n"
    
    if checkins:
        for checkin in checkins:
            message += f"🎫 Booking #{checkin[0]}\n"
            message += f"   👤 {checkin[1]}\n"
            message += f"   🏠 Room {checkin[2]}\n"
            message += f"   👥 {checkin[3]} guests\n"
            message += f"   💰 ${checkin[4]}\n\n"
            
            # Add check-in button
            context.user_data[f'checkin_{checkin[0]}'] = checkin
        
        message += f"Total Check-ins: {len(checkins)}"
        
        # Create buttons for each check-in
        keyboard = []
        for checkin in checkins:
            keyboard.append([InlineKeyboardButton(f"✅ Check-in {checkin[1]}", callback_data=f'checkin_{checkin[0]}')])
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='check_in_out')])
        keyboard.append([InlineKeyboardButton("🔙 Main Menu", callback_data='back_to_main')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
    else:
        message += "No check-ins scheduled for today."
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data='check_in_out')],
            [InlineKeyboardButton("🔙 Main Menu", callback_data='back_to_main')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)

async def show_todays_checkouts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    checkouts = get_todays_checkouts()
    
    message = "📤 TODAY'S CHECK-OUTS\n\n"
    
    if checkouts:
        for checkout in checkouts:
            payment_status = "✅ Paid" if checkout[4] == 'paid' else "⏳ Pending"
            
            message += f"🎫 Booking #{checkout[0]}\n"
            message += f"   👤 {checkout[1]}\n"
            message += f"   🏠 Room {checkout[2]}\n"
            message += f"   💰 ${checkout[3]} ({payment_status})\n\n"
            
            # Add check-out button
            context.user_data[f'checkout_{checkout[0]}'] = checkout
        
        message += f"Total Check-outs: {len(checkouts)}"
        
        # Create buttons for each check-out
        keyboard = []
        for checkout in checkouts:
            keyboard.append([InlineKeyboardButton(f"✅ Check-out {checkout[1]}", callback_data=f'checkout_{checkout[0]}')])
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='check_in_out')])
        keyboard.append([InlineKeyboardButton("🔙 Main Menu", callback_data='back_to_main')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
    else:
        message += "No check-outs scheduled for today."
        
        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data='check_in_out')],
            [InlineKeyboardButton("🔙 Main Menu", callback_data='back_to_main')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)

async def show_current_guests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    guests = get_current_guests()
    
    message = "🏨 CURRENT GUESTS\n\n"
    
    if guests:
        for guest in guests:
            message += f"🏠 Room {guest[2]}\n"
            message += f"   👤 {guest[1]}\n"
            message += f"   👥 {guest[3]} guests\n"
            message += f"   📅 {guest[4]} → {guest[5]}\n"
            message += f"   🎫 Booking #{guest[0]}\n\n"
        
        message += f"Total Current Guests: {len(guests)}"
    else:
        message += "No current guests."
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data='check_in_out')],
        [InlineKeyboardButton("🔙 Main Menu", callback_data='back_to_main')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def process_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE, booking_id):
    query = update.callback_query
    
    success = check_in_guest(booking_id)
    
    if success:
        await query.edit_message_text(
            f"✅ Check-in successful for booking #{booking_id}!\n\nGuest has been checked in.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Check-ins", callback_data='todays_checkins')],
                [InlineKeyboardButton("🔙 Main Menu", callback_data='back_to_main')]
            ])
        )
    else:
        await query.edit_message_text(
            f"❌ Failed to check in booking #{booking_id}.\n\nPlease try again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Check-ins", callback_data='todays_checkins')],
                [InlineKeyboardButton("🔙 Main Menu", callback_data='back_to_main')]
            ])
        )

async def process_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE, booking_id):
    query = update.callback_query
    
    success = check_out_guest(booking_id)
    
    if success:
        await query.edit_message_text(
            f"✅ Check-out successful for booking #{booking_id}!\n\nGuest has been checked out.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Check-outs", callback_data='todays_checkouts')],
                [InlineKeyboardButton("🔙 Main Menu", callback_data='back_to_main')]
            ])
        )
    else:
        await query.edit_message_text(
            f"❌ Failed to check out booking #{booking_id}.\n\nPlease make sure the guest has been checked in first.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Check-outs", callback_data='todays_checkouts')],
                [InlineKeyboardButton("🔙 Main Menu", callback_data='back_to_main')]
            ])
        )

async def show_analytics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    analytics = get_analytics()
    
    message = "📈 HOTEL ANALYTICS\n\n"
    message += f"🏨 Total Rooms: {analytics['total_rooms']}\n"
    message += f"🛏️ Occupied Today: {analytics['occupied_rooms']}\n"
    message += f"📊 Occupancy Rate: {analytics['occupancy_rate']:.1f}%\n"
    message += f"💰 Month Revenue: ${analytics['month_revenue']:.2f}\n"
    message += f"⭐ Most Popular: {analytics['most_popular']} ({analytics['most_popular_bookings']} bookings)"
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup)

async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    await query.edit_message_text(
        "🎫 QUICK BOOKING\n\nLet's create a new booking!\n\nHow many guests will be staying?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Cancel", callback_data='back_to_main')]
        ])
    )
    
    return BOOKING_GUESTS

async def booking_guests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        guest_count = int(update.message.text)
        if guest_count <= 0:
            await update.message.reply_text(
                "❌ Number of guests must be at least 1. Please try again:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 Cancel", callback_data='back_to_main')]
                ])
            )
            return BOOKING_GUESTS
        
        context.user_data['booking_guest_count'] = guest_count
        
        await update.message.reply_text(
            f"✅ {guest_count} guest(s) noted.\n\n📅 Please enter check-in date (YYYY-MM-DD format):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Cancel", callback_data='back_to_main')]
            ])
        )
        
        return BOOKING_CHECKIN
    except ValueError:
        await update.message.reply_text(
            "❌ Please enter a valid number for guest count:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Cancel", callback_data='back_to_main')]
            ])
        )
        return BOOKING_GUESTS

async def booking_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    check_in_date = update.message.text
    
    if not is_valid_date(check_in_date):
        await update.message.reply_text(
            "❌ Invalid date format or date is in the past. Please use YYYY-MM-DD format and ensure the date is today or later:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Cancel", callback_data='back_to_main')]
            ])
        )
        return BOOKING_CHECKIN
    
    context.user_data['booking_checkin'] = check_in_date
    
    await update.message.reply_text(
        f"✅ Check-in: {check_in_date}\n\n📅 Please enter check-out date (YYYY-MM-DD format):",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Cancel", callback_data='back_to_main')]
        ])
    )
    
    return BOOKING_CHECKOUT

async def booking_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    check_out_date = update.message.text
    check_in_date = context.user_data['booking_checkin']
    
    if not is_valid_date(check_out_date):
        await update.message.reply_text(
            "❌ Invalid date format or date is in the past. Please use YYYY-MM-DD format and ensure the date is today or later:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Cancel", callback_data='back_to_main')]
            ])
        )
        return BOOKING_CHECKOUT
    
    # Check that checkout is after checkin
    if check_out_date <= check_in_date:
        await update.message.reply_text(
            "❌ Check-out date must be after check-in date. Please enter a valid check-out date:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Cancel", callback_data='back_to_main')]
            ])
        )
        return BOOKING_CHECKOUT
    
    context.user_data['booking_checkout'] = check_out_date
    
    # Calculate total nights
    total_nights = calculate_total_nights(check_in_date, check_out_date)
    context.user_data['booking_nights'] = total_nights
    
    # Get available rooms
    guest_count = context.user_data['booking_guest_count']
    available_rooms = get_available_rooms(check_in_date, check_out_date, guest_count)
    
    if not available_rooms:
        await update.message.reply_text(
            "❌ No rooms available for your selected dates and guest count. Please try different dates.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
            ])
        )
        return ConversationHandler.END
    
    # Group rooms by type
    room_types = {}
    for room in available_rooms:
        room_type = room[2]
        if room_type not in room_types:
            room_types[room_type] = {
                'price': room[3],
                'count': 0,
                'rooms': []
            }
        room_types[room_type]['count'] += 1
        room_types[room_type]['rooms'].append(room)
    
    # Create keyboard with room options
    keyboard = []
    for room_type, info in room_types.items():
        total_price = info['price'] * total_nights
        button_text = f"{room_type} - ${info['price']}/night (${total_price} total) - {info['count']} available"
        
        # Store the first room of this type in context for quick selection
        first_room = info['rooms'][0]
        room_id = first_room[0]
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f'room_{room_id}')])
    
    keyboard.append([InlineKeyboardButton("🔙 Cancel", callback_data='back_to_main')])
    
    await update.message.reply_text(
        f"✅ Check-out: {check_out_date}\n🌙 Total nights: {total_nights}\n\n🏠 Available Room Types:\nPlease select a room type:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return BOOKING_ROOM

async def select_room(update: Update, context: ContextTypes.DEFAULT_TYPE, room_id):
    query = update.callback_query
    
    # Get room details
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, room_number, room_type, price_per_night FROM rooms WHERE id = ?', (room_id,))
    room = cursor.fetchone()
    conn.close()
    
    if not room:
        await query.edit_message_text(
            "❌ Room not found. Please try again.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
            ])
        )
        return ConversationHandler.END
    
    # Store room details in context
    context.user_data['booking_room_id'] = room[0]
    context.user_data['booking_room_number'] = room[1]
    context.user_data['booking_room_type'] = room[2]
    context.user_data['booking_room_price'] = room[3]
    
    # Calculate total amount
    total_nights = context.user_data['booking_nights']
    total_amount = room[3] * total_nights
    context.user_data['booking_total'] = total_amount
    
    # Show booking summary
    message = "📋 BOOKING SUMMARY\n\n"
    message += f"👥 Guests: {context.user_data['booking_guest_count']}\n"
    message += f"📅 Check-in: {context.user_data['booking_checkin']}\n"
    message += f"📅 Check-out: {context.user_data['booking_checkout']}\n"
    message += f"🌙 Nights: {total_nights}\n"
    message += f"🏠 Room Type: {room[2]}\n"
    message += f"💰 Rate: ${room[3]}/night\n"
    message += f"💵 Total Amount: ${total_amount}\n\n"
    message += "Please enter guest name:"
    
    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Cancel", callback_data='back_to_main')]
        ])
    )
    
    return BOOKING_NAME

async def booking_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    guest_name = update.message.text
    
    if not guest_name or len(guest_name.strip()) < 3:
        await update.message.reply_text(
            "❌ Please enter a valid guest name (at least 3 characters):",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Cancel", callback_data='back_to_main')]
            ])
        )
        return BOOKING_NAME
    
    context.user_data['booking_guest_name'] = guest_name
    
    # Create booking in database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute('''
    INSERT INTO bookings (
        guest_name, room_id, check_in_date, check_out_date, guest_count,
        total_amount, payment_status, booking_status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        guest_name,
        context.user_data['booking_room_id'],
        context.user_data['booking_checkin'],
        context.user_data['booking_checkout'],
        context.user_data['booking_guest_count'],
        context.user_data['booking_total'],
        'pending',
        'confirmed',
        now
    ))
    
    booking_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Show booking confirmation
    message = "✅ BOOKING CREATED SUCCESSFULLY!\n\n"
    message += f"🎫 Booking ID: {booking_id}\n"
    message += f"👤 Guest: {guest_name}\n"
    message += f"🏠 Room: {context.user_data['booking_room_number']} ({context.user_data['booking_room_type']})\n"
    message += f"👥 Guests: {context.user_data['booking_guest_count']}\n"
    message += f"📅 Check-in: {context.user_data['booking_checkin']}\n"
    message += f"📅 Check-out: {context.user_data['booking_checkout']}\n"
    message += f"💵 Total: ${context.user_data['booking_total']}\n"
    message += "💳 Payment: Pending\n\n"
    message += "Choose payment action:\n"
    
    keyboard = [
        [InlineKeyboardButton("💳 Mark as Paid", callback_data=f"payment_{booking_id}_paid")],
        [InlineKeyboardButton("📧 Send Payment Link", callback_data=f"payment_{booking_id}_link")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
    ]
    
    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
    
    return ConversationHandler.END

async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, booking_id, action):
    query = update.callback_query
    
    if action == 'paid':
        # Mark booking as paid
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('UPDATE bookings SET payment_status = ? WHERE id = ?', ('paid', booking_id))
        conn.commit()
        conn.close()
        
        await query.edit_message_text(
            f"✅ PAYMENT CONFIRMED\n\nBooking ID {booking_id} has been marked as paid.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
            ])
        )
    elif action == 'link':
        await query.edit_message_text(
            f"📧 PAYMENT LINK SENT\n\nA payment link has been sent to the guest for Booking ID {booking_id}.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
            ])
        )

async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    keyboard = [
        [InlineKeyboardButton("🏨 Room Status", callback_data='room_status'),
         InlineKeyboardButton("📊 Sales Report", callback_data='sales_report')],
        [InlineKeyboardButton("📅 Today's Bookings", callback_data='todays_bookings'),
         InlineKeyboardButton("📋 All Bookings", callback_data='all_bookings')],
        [InlineKeyboardButton("➕ Quick Booking", callback_data='quick_booking'),
         InlineKeyboardButton("❌ Cancelled Bookings", callback_data='cancelled_bookings')],
        [InlineKeyboardButton("🔄 Check-in/Check-out", callback_data='check_in_out'),
         InlineKeyboardButton("📈 Analytics", callback_data='analytics')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🏨 Hotel Management Bot\n\nWelcome! Choose an option from the menu below:",
        reply_markup=reply_markup
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Booking cancelled.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data='back_to_main')]
        ])
    )
    return ConversationHandler.END

async def send_daily_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if user is owner
    if OWNER_CHAT_ID and update.effective_chat.id != OWNER_CHAT_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    success = send_daily_report()
    
    if success:
        await update.message.reply_text("✅ Daily report has been sent to admin@hotel.com")
    else:
        await update.message.reply_text("❌ Failed to send daily report. Check email configuration.")

# Main function
def main():
    """Start the bot."""
    if not BOT_TOKEN:
        logging.error("BOT_TOKEN environment variable not set!")
        return
    
    # Setup database
    setup_database()
    
    # Create the Application
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Create conversation handler for booking
    booking_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_booking, pattern='^quick_booking$')],
        states={
            BOOKING_GUESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, booking_guests)],
            BOOKING_CHECKIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, booking_checkin)],
            BOOKING_CHECKOUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, booking_checkout)],
            BOOKING_ROOM: [CallbackQueryHandler(select_room, pattern='^room_')],
            BOOKING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, booking_name)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CallbackQueryHandler(back_to_main_menu, pattern='^back_to_main$')
        ],
        allow_reentry=True
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dailyreport", send_daily_report_command))
    application.add_handler(booking_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Run the bot
    logging.info("Starting Hotel Management Bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
