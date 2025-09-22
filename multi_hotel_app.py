import os
import logging
import sqlite3
import datetime
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import telegram_bot

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Database setup
DB_NAME = 'multi_hotel.db'

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create admin users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Create hotels table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hotels (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        telegram_number TEXT,
        telegram_bot_token TEXT,
        telegram_chat_id TEXT,
        owner_name TEXT NOT NULL,
        owner_email TEXT NOT NULL,
        owner_phone TEXT,
        created_at TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1
    )
    ''')
    
    # Create hotel owners table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hotel_owners (
        id INTEGER PRIMARY KEY,
        hotel_id INTEGER NOT NULL,
        username TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        phone TEXT,
        created_at TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        FOREIGN KEY (hotel_id) REFERENCES hotels (id)
    )
    ''')
    
    # Create rooms table (modified to include hotel_id)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY,
        hotel_id INTEGER NOT NULL,
        room_number TEXT NOT NULL,
        room_type TEXT NOT NULL,
        price_per_night REAL NOT NULL,
        capacity INTEGER NOT NULL,
        amenities TEXT,
        is_active BOOLEAN DEFAULT 1,
        created_at TEXT NOT NULL,
        FOREIGN KEY (hotel_id) REFERENCES hotels (id),
        UNIQUE(hotel_id, room_number)
    )
    ''')
    
    # Create room categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS room_categories (
        id INTEGER PRIMARY KEY,
        hotel_id INTEGER NOT NULL,
        category_name TEXT NOT NULL,
        description TEXT,
        base_price REAL NOT NULL,
        max_occupancy INTEGER NOT NULL,
        amenities TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (hotel_id) REFERENCES hotels (id),
        UNIQUE(hotel_id, category_name)
    )
    ''')
    
    # Create bookings table (modified to include hotel_id)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY,
        hotel_id INTEGER NOT NULL,
        guest_name TEXT NOT NULL,
        guest_email TEXT,
        guest_phone TEXT,
        room_id INTEGER NOT NULL,
        check_in_date TEXT NOT NULL,
        check_out_date TEXT NOT NULL,
        guest_count INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        payment_status TEXT DEFAULT 'pending',
        booking_status TEXT DEFAULT 'confirmed',
        special_requests TEXT,
        created_at TEXT NOT NULL,
        cancelled_at TEXT,
        FOREIGN KEY (hotel_id) REFERENCES hotels (id),
        FOREIGN KEY (room_id) REFERENCES rooms (id)
    )
    ''')
    
    # Create check_in_out table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS check_in_out (
        id INTEGER PRIMARY KEY,
        booking_id INTEGER NOT NULL,
        check_in_time TEXT,
        check_out_time TEXT,
        notes TEXT,
        FOREIGN KEY (booking_id) REFERENCES bookings (id)
    )
    ''')
    
    # Create default admin user if not exists
    cursor.execute('SELECT COUNT(*) FROM admin_users')
    if cursor.fetchone()[0] == 0:
        admin_password = generate_password_hash('admin123')
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
        INSERT INTO admin_users (username, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin@hotel.com', admin_password, now))
    
    conn.commit()
    conn.close()

# Authentication helpers
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def owner_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'owner':
            flash('Hotel owner access required', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        if session['user_type'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session['user_type'] == 'owner':
            return redirect(url_for('owner_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        if user_type == 'admin':
            cursor.execute('SELECT id, password_hash FROM admin_users WHERE username = ? AND is_active = 1', (username,))
        else:
            cursor.execute('SELECT id, password_hash, hotel_id FROM hotel_owners WHERE username = ? AND is_active = 1', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['user_type'] = user_type
            session['username'] = username
            if user_type == 'owner':
                session['hotel_id'] = user[2]
            
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get total hotels
    cursor.execute('SELECT COUNT(*) FROM hotels WHERE is_active = 1')
    total_hotels = cursor.fetchone()[0]
    
    # Get total rooms across all hotels
    cursor.execute('SELECT COUNT(*) FROM rooms WHERE is_active = 1')
    total_rooms = cursor.fetchone()[0]
    
    # Get total bookings this month
    month_start = datetime.datetime.now().replace(day=1).strftime("%Y-%m-%d")
    cursor.execute('SELECT COUNT(*) FROM bookings WHERE created_at >= ? AND booking_status = "confirmed"', (month_start,))
    monthly_bookings = cursor.fetchone()[0]
    
    # Get total revenue this month
    cursor.execute('SELECT SUM(total_amount) FROM bookings WHERE created_at >= ? AND booking_status = "confirmed" AND payment_status = "paid"', (month_start,))
    monthly_revenue = cursor.fetchone()[0] or 0
    
    # Get recent hotels
    cursor.execute('SELECT id, name, owner_name, owner_email, created_at FROM hotels WHERE is_active = 1 ORDER BY created_at DESC LIMIT 5')
    recent_hotels = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         total_hotels=total_hotels,
                         total_rooms=total_rooms,
                         monthly_bookings=monthly_bookings,
                         monthly_revenue=monthly_revenue,
                         recent_hotels=recent_hotels)

@app.route('/admin/hotels')
@login_required
@admin_required
def admin_hotels():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT h.id, h.name, h.address, h.owner_name, h.owner_email, h.telegram_number, h.created_at,
           COUNT(r.id) as room_count
    FROM hotels h
    LEFT JOIN rooms r ON h.id = r.hotel_id AND r.is_active = 1
    WHERE h.is_active = 1
    GROUP BY h.id
    ORDER BY h.created_at DESC
    ''')
    
    hotels = cursor.fetchall()
    conn.close()
    
    return render_template('admin_hotels.html', hotels=hotels)

@app.route('/admin/add_hotel', methods=['GET', 'POST'])
@login_required
@admin_required
def add_hotel():
    if request.method == 'POST':
        # Hotel details
        hotel_name = request.form['hotel_name']
        hotel_address = request.form['hotel_address']
        hotel_phone = request.form['hotel_phone']
        hotel_email = request.form['hotel_email']
        telegram_number = request.form['telegram_number']
        
        # Owner details
        owner_name = request.form['owner_name']
        owner_email = request.form['owner_email']
        owner_phone = request.form['owner_phone']
        owner_username = request.form['owner_username']
        owner_password = request.form['owner_password']
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert hotel
            telegram_bot_token = request.form.get('telegram_bot_token', '')
            telegram_chat_id = request.form.get('telegram_chat_id', '')
            
            cursor.execute('''
            INSERT INTO hotels (name, address, phone, email, telegram_number, telegram_bot_token, telegram_chat_id, owner_name, owner_email, owner_phone, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (hotel_name, hotel_address, hotel_phone, hotel_email, telegram_number, telegram_bot_token, telegram_chat_id, owner_name, owner_email, owner_phone, now))
            
            hotel_id = cursor.lastrowid
            
            # Insert hotel owner
            password_hash = generate_password_hash(owner_password)
            cursor.execute('''
            INSERT INTO hotel_owners (hotel_id, username, email, password_hash, full_name, phone, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (hotel_id, owner_username, owner_email, password_hash, owner_name, owner_phone, now))
            
            conn.commit()
            flash('Hotel and owner account created successfully!', 'success')
            return redirect(url_for('admin_hotels'))
            
        except sqlite3.IntegrityError as e:
            flash('Error: Username or email already exists', 'error')
        except Exception as e:
            flash(f'Error creating hotel: {str(e)}', 'error')
        finally:
            conn.close()
    
    return render_template('add_hotel.html')

@app.route('/owner/dashboard')
@login_required
@owner_required
def owner_dashboard():
    hotel_id = session['hotel_id']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get hotel info
    cursor.execute('SELECT name FROM hotels WHERE id = ?', (hotel_id,))
    hotel_name = cursor.fetchone()[0]
    
    # Get total rooms
    cursor.execute('SELECT COUNT(*) FROM rooms WHERE hotel_id = ? AND is_active = 1', (hotel_id,))
    total_rooms = cursor.fetchone()[0]
    
    # Get occupied rooms today
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    cursor.execute('''
    SELECT COUNT(DISTINCT r.id)
    FROM rooms r
    JOIN bookings b ON r.id = b.room_id
    WHERE r.hotel_id = ? AND b.booking_status = 'confirmed'
    AND b.check_in_date <= ? AND b.check_out_date > ?
    ''', (hotel_id, today, today))
    occupied_rooms = cursor.fetchone()[0]
    
    # Get today's bookings
    cursor.execute('''
    SELECT COUNT(*) FROM bookings 
    WHERE hotel_id = ? AND check_in_date = ? AND booking_status = 'confirmed'
    ''', (hotel_id, today))
    today_bookings = cursor.fetchone()[0]
    
    # Get monthly revenue
    month_start = datetime.datetime.now().replace(day=1).strftime("%Y-%m-%d")
    cursor.execute('''
    SELECT SUM(total_amount) FROM bookings 
    WHERE hotel_id = ? AND created_at >= ? AND booking_status = 'confirmed' AND payment_status = 'paid'
    ''', (hotel_id, month_start))
    monthly_revenue = cursor.fetchone()[0] or 0
    
    # Get recent bookings
    cursor.execute('''
    SELECT b.id, b.guest_name, r.room_number, b.check_in_date, b.check_out_date, b.total_amount, b.payment_status
    FROM bookings b
    JOIN rooms r ON b.room_id = r.id
    WHERE b.hotel_id = ? AND b.booking_status = 'confirmed'
    ORDER BY b.created_at DESC LIMIT 5
    ''', (hotel_id,))
    recent_bookings = cursor.fetchall()
    
    conn.close()
    
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    return render_template('owner_dashboard.html',
                         hotel_name=hotel_name,
                         total_rooms=total_rooms,
                         occupied_rooms=occupied_rooms,
                         occupancy_rate=occupancy_rate,
                         today_bookings=today_bookings,
                         monthly_revenue=monthly_revenue,
                         recent_bookings=recent_bookings)

@app.route('/owner/rooms')
@login_required
@owner_required
def owner_rooms():
    hotel_id = session['hotel_id']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT r.id, r.room_number, r.room_type, r.price_per_night, r.capacity, r.amenities, r.is_active,
           COUNT(b.id) as booking_count
    FROM rooms r
    LEFT JOIN bookings b ON r.id = b.room_id AND b.booking_status = 'confirmed'
    WHERE r.hotel_id = ?
    GROUP BY r.id
    ORDER BY r.room_number
    ''', (hotel_id,))
    
    rooms = cursor.fetchall()
    conn.close()
    
    return render_template('owner_rooms.html', rooms=rooms)

@app.route('/owner/bookings')
@login_required
@owner_required
def owner_bookings():
    hotel_id = session['hotel_id']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT b.id, b.guest_name, b.guest_email, b.guest_phone, r.room_number, 
           b.check_in_date, b.check_out_date, b.guest_count, b.total_amount, 
           b.payment_status, b.booking_status, b.created_at
    FROM bookings b
    JOIN rooms r ON b.room_id = r.id
    WHERE b.hotel_id = ?
    ORDER BY b.created_at DESC
    ''', (hotel_id,))
    
    bookings = cursor.fetchall()
    conn.close()
    
    return render_template('owner_bookings.html', bookings=bookings)

@app.route('/owner/checkin-checkout')
@login_required
@owner_required
def owner_checkin_checkout():
    hotel_id = session['hotel_id']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Get today's check-ins
    cursor.execute('''
    SELECT b.id, b.guest_name, r.room_number, b.guest_count, b.total_amount,
           c.check_in_time
    FROM bookings b
    JOIN rooms r ON b.room_id = r.id
    LEFT JOIN check_in_out c ON b.id = c.booking_id
    WHERE b.hotel_id = ? AND b.check_in_date = ? AND b.booking_status = 'confirmed'
    ORDER BY b.created_at
    ''', (hotel_id, today))
    
    checkins = cursor.fetchall()
    
    # Get today's check-outs
    cursor.execute('''
    SELECT b.id, b.guest_name, r.room_number, b.total_amount, b.payment_status,
           c.check_in_time, c.check_out_time
    FROM bookings b
    JOIN rooms r ON b.room_id = r.id
    LEFT JOIN check_in_out c ON b.id = c.booking_id
    WHERE b.hotel_id = ? AND b.check_out_date = ? AND b.booking_status = 'confirmed'
    ORDER BY b.created_at
    ''', (hotel_id, today))
    
    checkouts = cursor.fetchall()
    
    conn.close()
    
    return render_template('owner_checkin_checkout.html', checkins=checkins, checkouts=checkouts)

@app.route('/admin/hotels/<int:hotel_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_hotel(hotel_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Get current status
        cursor.execute('SELECT is_active FROM hotels WHERE id = ?', (hotel_id,))
        result = cursor.fetchone()
        if not result:
            flash('Hotel not found', 'error')
            return redirect(url_for('admin_hotels'))
        
        current_status = result[0]
        new_status = 0 if current_status else 1
        
        # Update status
        cursor.execute('UPDATE hotels SET is_active = ? WHERE id = ?', (new_status, hotel_id))
        conn.commit()
        
        status_text = "activated" if new_status else "deactivated"
        flash(f'Hotel {status_text} successfully!', 'success')
    except Exception as e:
        flash(f'Error toggling hotel status: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin_hotels'))

@app.route('/admin/hotels/<int:hotel_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_hotel(hotel_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Delete in order due to foreign key constraints
        cursor.execute('DELETE FROM check_in_out WHERE booking_id IN (SELECT id FROM bookings WHERE hotel_id = ?)', (hotel_id,))
        cursor.execute('DELETE FROM bookings WHERE hotel_id = ?', (hotel_id,))
        cursor.execute('DELETE FROM rooms WHERE hotel_id = ?', (hotel_id,))
        cursor.execute('DELETE FROM room_categories WHERE hotel_id = ?', (hotel_id,))
        cursor.execute('DELETE FROM hotel_owners WHERE hotel_id = ?', (hotel_id,))
        cursor.execute('DELETE FROM hotels WHERE id = ?', (hotel_id,))
        
        conn.commit()
        flash('Hotel deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting hotel: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin_hotels'))

@app.route('/admin/hotels/<int:hotel_id>/test-telegram', methods=['POST'])
@login_required
@admin_required
def test_telegram_connection(hotel_id):
    """Test Telegram bot connection for a hotel."""
    try:
        test_message = f"🤖 Test message from Hotel Management System\n\nThis is a test to verify your Telegram bot connection is working properly.\n\nTime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        success = telegram_bot.send_notification(hotel_id, test_message)
        
        if success:
            flash('Test message sent successfully! Check your Telegram chat.', 'success')
        else:
            flash('Failed to send test message. Please check your Telegram configuration.', 'error')
    except Exception as e:
        flash(f'Error testing Telegram connection: {str(e)}', 'error')
    
    return redirect(url_for('view_hotel', hotel_id=hotel_id))

@app.route('/telegram-setup')
def telegram_setup():
    """Show Telegram setup instructions."""
    return render_template('telegram_setup.html')

@app.route('/admin/hotels/<int:hotel_id>')
@login_required
@admin_required
def view_hotel(hotel_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get hotel details with proper column order
    cursor.execute('''
    SELECT id, name, address, phone, email, telegram_number, telegram_bot_token, 
           owner_name, owner_email, owner_phone, created_at, is_active, telegram_chat_id
    FROM hotels WHERE id = ?
    ''', (hotel_id,))
    hotel = cursor.fetchone()
    
    if not hotel:
        flash('Hotel not found', 'error')
        return redirect(url_for('admin_hotels'))
    
    # Get hotel owner
    cursor.execute('SELECT * FROM hotel_owners WHERE hotel_id = ?', (hotel_id,))
    owner = cursor.fetchone()
    
    # Get rooms count
    cursor.execute('SELECT COUNT(*) FROM rooms WHERE hotel_id = ? AND is_active = 1', (hotel_id,))
    rooms_count = cursor.fetchone()[0]
    
    # Get bookings count
    cursor.execute('SELECT COUNT(*) FROM bookings WHERE hotel_id = ? AND booking_status = "confirmed"', (hotel_id,))
    bookings_count = cursor.fetchone()[0]
    
    conn.close()
    
    return render_template('view_hotel.html', hotel=hotel, owner=owner, 
                         rooms_count=rooms_count, bookings_count=bookings_count)

@app.route('/admin/hotels/<int:hotel_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_hotel(hotel_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Update hotel details
        hotel_name = request.form['hotel_name']
        hotel_address = request.form['hotel_address']
        hotel_phone = request.form['hotel_phone']
        hotel_email = request.form['hotel_email']
        telegram_number = request.form['telegram_number']
        telegram_bot_token = request.form.get('telegram_bot_token', '')
        telegram_chat_id = request.form.get('telegram_chat_id', '')
        owner_name = request.form['owner_name']
        owner_email = request.form['owner_email']
        owner_phone = request.form['owner_phone']
        
        try:
            cursor.execute('''
            UPDATE hotels SET name = ?, address = ?, phone = ?, email = ?, 
                   telegram_number = ?, telegram_bot_token = ?, telegram_chat_id = ?,
                   owner_name = ?, owner_email = ?, owner_phone = ?
            WHERE id = ?
            ''', (hotel_name, hotel_address, hotel_phone, hotel_email, telegram_number,
                  telegram_bot_token, telegram_chat_id, owner_name, owner_email, owner_phone, hotel_id))
            
            conn.commit()
            flash('Hotel updated successfully!', 'success')
            return redirect(url_for('view_hotel', hotel_id=hotel_id))
        except Exception as e:
            flash(f'Error updating hotel: {str(e)}', 'error')
    
    # Get hotel details for form with proper column names
    cursor.execute('''
    SELECT id, name, address, phone, email, telegram_number, telegram_bot_token, 
           owner_name, owner_email, owner_phone, created_at, is_active, telegram_chat_id
    FROM hotels WHERE id = ?
    ''', (hotel_id,))
    hotel = cursor.fetchone()
    
    conn.close()
    
    if not hotel:
        flash('Hotel not found', 'error')
        return redirect(url_for('admin_hotels'))
    
    return render_template('edit_hotel.html', hotel=hotel)

@app.route('/owner/add-booking', methods=['GET', 'POST'])
@login_required
@owner_required
def add_booking():
    hotel_id = session['hotel_id']
    
    if request.method == 'POST':
        # Handle booking creation
        guest_name = request.form['guest_name']
        guest_email = request.form['guest_email']
        guest_phone = request.form['guest_phone']
        room_id = request.form['room_id']
        check_in_date = request.form['check_in_date']
        check_out_date = request.form['check_out_date']
        guest_count = int(request.form['guest_count'])
        special_requests = request.form.get('special_requests', '')
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        try:
            # Get room price
            cursor.execute('SELECT price_per_night FROM rooms WHERE id = ? AND hotel_id = ?', (room_id, hotel_id))
            room_price = cursor.fetchone()[0]
            
            # Calculate total amount
            check_in = datetime.datetime.strptime(check_in_date, '%Y-%m-%d')
            check_out = datetime.datetime.strptime(check_out_date, '%Y-%m-%d')
            nights = (check_out - check_in).days
            total_amount = room_price * nights
            
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
            INSERT INTO bookings (hotel_id, guest_name, guest_email, guest_phone, room_id,
                                check_in_date, check_out_date, guest_count, total_amount,
                                special_requests, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (hotel_id, guest_name, guest_email, guest_phone, room_id,
                  check_in_date, check_out_date, guest_count, total_amount,
                  special_requests, now))
            
            booking_id = cursor.lastrowid
            
            # Get room details for notification
            cursor.execute('SELECT room_number FROM rooms WHERE id = ?', (room_id,))
            room_number = cursor.fetchone()[0]
            
            conn.commit()
            
            # Send Telegram notification
            try:
                notification_message = f"""
🏨 New Booking Alert!

Guest: {guest_name}
Room: {room_number}
Check-in: {check_in_date}
Check-out: {check_out_date}
Guests: {guest_count}
Total Amount: ${total_amount:.2f}

Booking ID: {booking_id}
                """.strip()
                
                telegram_bot.send_notification(hotel_id, notification_message)
            except Exception as e:
                logging.error(f"Failed to send booking notification: {e}")
            
            flash('Booking created successfully!', 'success')
            return redirect(url_for('owner_bookings'))
            
        except Exception as e:
            flash(f'Error creating booking: {str(e)}', 'error')
        finally:
            conn.close()
    
    # Get available rooms
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id, room_number, room_type, price_per_night, capacity FROM rooms WHERE hotel_id = ? AND is_active = 1', (hotel_id,))
    rooms = cursor.fetchall()
    conn.close()
    
    return render_template('add_booking.html', rooms=rooms)

# Additional routes for room management
@app.route('/owner/rooms/add', methods=['GET', 'POST'])
@login_required
@owner_required
def add_room():
    hotel_id = session['hotel_id']
    
    if request.method == 'POST':
        room_number = request.form['room_number']
        room_type = request.form['room_type']
        price_per_night = float(request.form['price_per_night'])
        capacity = int(request.form['capacity'])
        amenities = request.form.get('amenities', '')
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
            INSERT INTO rooms (hotel_id, room_number, room_type, price_per_night, capacity, amenities, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (hotel_id, room_number, room_type, price_per_night, capacity, amenities, now))
            
            conn.commit()
            flash('Room added successfully!', 'success')
            return redirect(url_for('owner_rooms'))
            
        except sqlite3.IntegrityError:
            flash('Room number already exists!', 'error')
        except Exception as e:
            flash(f'Error adding room: {str(e)}', 'error')
        finally:
            conn.close()
    
    return render_template('add_room.html')

@app.route('/owner/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_room(room_id):
    hotel_id = session['hotel_id']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        room_number = request.form['room_number']
        room_type = request.form['room_type']
        price_per_night = float(request.form['price_per_night'])
        capacity = int(request.form['capacity'])
        amenities = request.form.get('amenities', '')
        
        try:
            cursor.execute('''
            UPDATE rooms SET room_number = ?, room_type = ?, price_per_night = ?, 
                   capacity = ?, amenities = ?
            WHERE id = ? AND hotel_id = ?
            ''', (room_number, room_type, price_per_night, capacity, amenities, room_id, hotel_id))
            
            conn.commit()
            flash('Room updated successfully!', 'success')
            return redirect(url_for('owner_rooms'))
            
        except sqlite3.IntegrityError:
            flash('Room number already exists!', 'error')
        except Exception as e:
            flash(f'Error updating room: {str(e)}', 'error')
    
    # Get room details
    cursor.execute('SELECT * FROM rooms WHERE id = ? AND hotel_id = ?', (room_id, hotel_id))
    room = cursor.fetchone()
    conn.close()
    
    if not room:
        flash('Room not found', 'error')
        return redirect(url_for('owner_rooms'))
    
    return render_template('edit_room.html', room=room)

@app.route('/owner/rooms/<int:room_id>/toggle', methods=['POST'])
@login_required
@owner_required
def toggle_room_status(room_id):
    hotel_id = session['hotel_id']
    data = request.get_json()
    status = data.get('status', True)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE rooms SET is_active = ? WHERE id = ? AND hotel_id = ?', 
                      (status, room_id, hotel_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@app.route('/owner/rooms/<int:room_id>/delete')
@login_required
@owner_required
def delete_room(room_id):
    hotel_id = session['hotel_id']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Check if room has active bookings
        cursor.execute('''
        SELECT COUNT(*) FROM bookings 
        WHERE room_id = ? AND booking_status = 'confirmed' 
        AND check_out_date >= date('now')
        ''', (room_id,))
        
        active_bookings = cursor.fetchone()[0]
        
        if active_bookings > 0:
            flash('Cannot delete room with active bookings!', 'error')
        else:
            cursor.execute('DELETE FROM rooms WHERE id = ? AND hotel_id = ?', (room_id, hotel_id))
            conn.commit()
            flash('Room deleted successfully!', 'success')
            
    except Exception as e:
        flash(f'Error deleting room: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('owner_rooms'))

# Booking management routes
@app.route('/owner/bookings/<int:booking_id>/details')
@login_required
@owner_required
def booking_details(booking_id):
    hotel_id = session['hotel_id']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT b.*, r.room_number, r.room_type, c.check_in_time, c.check_out_time, c.notes
    FROM bookings b
    JOIN rooms r ON b.room_id = r.id
    LEFT JOIN check_in_out c ON b.id = c.booking_id
    WHERE b.id = ? AND b.hotel_id = ?
    ''', (booking_id, hotel_id))
    
    booking = cursor.fetchone()
    conn.close()
    
    if not booking:
        return jsonify({'error': 'Booking not found'})
    
    # Calculate nights
    check_in = datetime.datetime.strptime(booking[5], '%Y-%m-%d')
    check_out = datetime.datetime.strptime(booking[6], '%Y-%m-%d')
    nights = (check_out - check_in).days
    
    html = f'''
    <div class="row">
        <div class="col-md-6">
            <h6>Guest Information</h6>
            <p><strong>Name:</strong> {booking[2]}</p>
            <p><strong>Email:</strong> {booking[3] or 'Not provided'}</p>
            <p><strong>Phone:</strong> {booking[4] or 'Not provided'}</p>
            <p><strong>Guest Count:</strong> {booking[7]}</p>
        </div>
        <div class="col-md-6">
            <h6>Booking Details</h6>
            <p><strong>Room:</strong> {booking[14]} ({booking[15]})</p>
            <p><strong>Check-in:</strong> {booking[5]}</p>
            <p><strong>Check-out:</strong> {booking[6]}</p>
            <p><strong>Nights:</strong> {nights}</p>
            <p><strong>Total Amount:</strong> ₹{booking[8]:.2f}</p>
        </div>
    </div>
    <div class="row mt-3">
        <div class="col-12">
            <h6>Status</h6>
            <p><strong>Booking Status:</strong> <span class="badge bg-{"success" if booking[10] == "confirmed" else "danger"}">{booking[10].title()}</span></p>
            <p><strong>Payment Status:</strong> <span class="badge bg-{"success" if booking[9] == "paid" else "warning"}">{booking[9].title()}</span></p>
            <p><strong>Created:</strong> {booking[12]}</p>
        </div>
    </div>
    '''
    
    if booking[11]:  # special_requests
        html += f'<div class="row mt-3"><div class="col-12"><h6>Special Requests</h6><p>{booking[11]}</p></div></div>'
    
    if booking[16] or booking[17]:  # check-in/out times
        html += '<div class="row mt-3"><div class="col-12"><h6>Check-in/out Status</h6>'
        if booking[16]:
            html += f'<p><strong>Checked In:</strong> {booking[16]}</p>'
        if booking[17]:
            html += f'<p><strong>Checked Out:</strong> {booking[17]}</p>'
        if booking[18]:
            html += f'<p><strong>Notes:</strong> {booking[18]}</p>'
        html += '</div></div>'
    
    return jsonify({'html': html})

@app.route('/owner/bookings/<int:booking_id>/mark-paid', methods=['POST'])
@login_required
@owner_required
def mark_booking_paid(booking_id):
    hotel_id = session['hotel_id']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        UPDATE bookings SET payment_status = 'paid' 
        WHERE id = ? AND hotel_id = ? AND booking_status = 'confirmed'
        ''', (booking_id, hotel_id))
        
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@app.route('/owner/bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
@owner_required
def cancel_booking(booking_id):
    hotel_id = session['hotel_id']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
        UPDATE bookings SET booking_status = 'cancelled', cancelled_at = ?
        WHERE id = ? AND hotel_id = ?
        ''', (now, booking_id, hotel_id))
        
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@app.route('/owner/bookings/<int:booking_id>/checkin', methods=['POST'])
@login_required
@owner_required
def checkin_guest(booking_id):
    hotel_id = session['hotel_id']
    data = request.get_json()
    notes = data.get('notes', '')
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if record exists
        cursor.execute('SELECT id FROM check_in_out WHERE booking_id = ?', (booking_id,))
        record = cursor.fetchone()
        
        if record:
            cursor.execute('''
            UPDATE check_in_out SET check_in_time = ?, notes = ?
            WHERE booking_id = ?
            ''', (now, notes, booking_id))
        else:
            cursor.execute('''
            INSERT INTO check_in_out (booking_id, check_in_time, notes)
            VALUES (?, ?, ?)
            ''', (booking_id, now, notes))
        
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@app.route('/owner/bookings/<int:booking_id>/checkout', methods=['POST'])
@login_required
@owner_required
def checkout_guest(booking_id):
    hotel_id = session['hotel_id']
    data = request.get_json()
    notes = data.get('notes', '')
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
        UPDATE check_in_out SET check_out_time = ?, notes = COALESCE(notes || ' | ', '') || ?
        WHERE booking_id = ?
        ''', (now, notes, booking_id))
        
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()

@app.route('/owner/current-guests')
@login_required
@owner_required
def current_guests():
    hotel_id = session['hotel_id']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    cursor.execute('''
    SELECT b.guest_name, r.room_number, b.guest_count, b.check_in_date, b.check_out_date
    FROM bookings b
    JOIN rooms r ON b.room_id = r.id
    JOIN check_in_out c ON b.id = c.booking_id
    WHERE b.hotel_id = ? AND b.booking_status = 'confirmed'
    AND c.check_in_time IS NOT NULL AND c.check_out_time IS NULL
    AND b.check_out_date >= ?
    ORDER BY r.room_number
    ''', (hotel_id, today))
    
    guests = cursor.fetchall()
    conn.close()
    
    guest_list = []
    for guest in guests:
        guest_list.append({
            'name': guest[0],
            'room': guest[1],
            'guests': guest[2],
            'checkin_date': guest[3],
            'checkout_date': guest[4]
        })
    
    return jsonify({'guests': guest_list})

@app.route('/owner/bookings/<int:booking_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_booking(booking_id):
    hotel_id = session['hotel_id']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        guest_name = request.form['guest_name']
        guest_email = request.form['guest_email']
        guest_phone = request.form['guest_phone']
        room_id = request.form['room_id']
        check_in_date = request.form['check_in_date']
        check_out_date = request.form['check_out_date']
        guest_count = int(request.form['guest_count'])
        special_requests = request.form.get('special_requests', '')
        
        try:
            # Get room price
            cursor.execute('SELECT price_per_night FROM rooms WHERE id = ? AND hotel_id = ?', (room_id, hotel_id))
            room_price = cursor.fetchone()[0]
            
            # Calculate total amount
            check_in = datetime.datetime.strptime(check_in_date, '%Y-%m-%d')
            check_out = datetime.datetime.strptime(check_out_date, '%Y-%m-%d')
            nights = (check_out - check_in).days
            total_amount = room_price * nights
            
            cursor.execute('''
            UPDATE bookings SET guest_name = ?, guest_email = ?, guest_phone = ?, room_id = ?,
                   check_in_date = ?, check_out_date = ?, guest_count = ?, total_amount = ?,
                   special_requests = ?
            WHERE id = ? AND hotel_id = ?
            ''', (guest_name, guest_email, guest_phone, room_id, check_in_date, check_out_date,
                  guest_count, total_amount, special_requests, booking_id, hotel_id))
            
            conn.commit()
            flash('Booking updated successfully!', 'success')
            return redirect(url_for('owner_bookings'))
            
        except Exception as e:
            flash(f'Error updating booking: {str(e)}', 'error')
    
    # Get booking details
    cursor.execute('''
    SELECT b.*, r.room_number FROM bookings b
    JOIN rooms r ON b.room_id = r.id
    WHERE b.id = ? AND b.hotel_id = ?
    ''', (booking_id, hotel_id))
    booking = cursor.fetchone()
    
    if not booking:
        flash('Booking not found', 'error')
        return redirect(url_for('owner_bookings'))
    
    # Get available rooms
    cursor.execute('SELECT id, room_number, room_type, price_per_night, capacity FROM rooms WHERE hotel_id = ? AND is_active = 1', (hotel_id,))
    rooms = cursor.fetchall()
    
    conn.close()
    
    return render_template('edit_booking.html', booking=booking, rooms=rooms)

@app.route('/owner/categories')
@login_required
@owner_required
def manage_categories():
    hotel_id = session['hotel_id']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM room_categories WHERE hotel_id = ? ORDER BY category_name', (hotel_id,))
    categories = cursor.fetchall()
    conn.close()
    
    return render_template('manage_categories.html', categories=categories)

if __name__ == '__main__':
    setup_database()
    app.run(debug=True, port=5000)