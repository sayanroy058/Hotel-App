# Multi-Hotel Management System

A comprehensive hotel management platform that allows system administrators to manage multiple hotels and hotel owners to manage their individual properties. Built with Flask, SQLite, and modern web technologies.

## 🌟 Features

### Admin Dashboard
- **Multi-Hotel Management**: Add, edit, and manage multiple hotels
- **Owner Account Creation**: Automatically create login credentials for hotel owners
- **System Overview**: View total hotels, rooms, bookings, and revenue across all properties
- **Telegram Integration**: Setup Telegram bot numbers for each hotel
- **Centralized Control**: Monitor and manage all hotels from one dashboard

### Hotel Owner Dashboard
- **Property Management**: Complete control over their hotel operations
- **Room Management**: Add, edit, delete, and categorize rooms
- **Booking System**: Create, modify, and cancel bookings
- **Check-in/Check-out**: Manage guest arrivals and departures
- **Revenue Tracking**: Monitor bookings and payments
- **Guest Management**: Track current guests and their details

### Key Capabilities
- **Multi-tenant Architecture**: Each hotel operates independently
- **Role-based Access**: Admin and hotel owner roles with appropriate permissions
- **Real-time Dashboard**: Live statistics and occupancy rates
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Secure Authentication**: Password hashing and session management
- **Database Integrity**: Foreign key constraints and data validation

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Admin Panel   │    │  Hotel Owner    │    │   Database      │
│                 │    │   Dashboard     │    │                 │
│ • Manage Hotels │    │ • Manage Rooms  │    │ • Hotels        │
│ • Create Owners │    │ • Bookings      │    │ • Rooms         │
│ • System Stats  │    │ • Check-in/out  │    │ • Bookings      │
│ • Monitoring    │    │ • Revenue       │    │ • Users         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📋 Database Schema

### Core Tables
- **admin_users**: System administrators
- **hotels**: Hotel properties and details
- **hotel_owners**: Hotel owner accounts
- **rooms**: Room inventory for each hotel
- **room_categories**: Room type definitions
- **bookings**: Guest reservations
- **check_in_out**: Guest arrival/departure tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment (optional)**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the application**:
   ```bash
   python run.py
   ```

5. **Access the system**:
   - Open http://localhost:5000
   - Login as admin: `admin` / `admin123`

## 👥 User Roles & Access

### System Admin
- **Username**: `admin`
- **Password**: `admin123` (change in production)
- **Capabilities**:
  - Add/edit/delete hotels
  - Create hotel owner accounts
  - View system-wide statistics
  - Monitor all hotel operations

### Hotel Owners
- **Created by**: System admin
- **Capabilities**:
  - Manage their hotel's rooms
  - Handle bookings and reservations
  - Check-in/check-out guests
  - View revenue and statistics
  - Update room prices and availability

## 🏨 Hotel Management Workflow

### For Admins
1. **Add New Hotel**:
   - Enter hotel details (name, address, contact)
   - Set up owner information
   - Create login credentials
   - Configure Telegram integration (optional)

2. **Monitor System**:
   - View dashboard with all hotels
   - Track total rooms and bookings
   - Monitor revenue across properties

### For Hotel Owners
1. **Setup Rooms**:
   - Add room numbers and types
   - Set pricing and capacity
   - Define amenities

2. **Manage Bookings**:
   - Create new reservations
   - Modify existing bookings
   - Handle cancellations
   - Track payments

3. **Daily Operations**:
   - Check-in arriving guests
   - Check-out departing guests
   - Monitor occupancy rates
   - View revenue reports

## 🔧 Configuration

### Environment Variables (.env)
```env
SECRET_KEY=your-secret-key-here
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
BOT_TOKEN=your-telegram-bot-token
OWNER_CHAT_ID=your-telegram-chat-id
```

### Database Configuration
- **Type**: SQLite (default)
- **File**: `multi_hotel.db`
- **Auto-created**: Yes, on first run

## 📱 Features in Detail

### Room Management
- **Room Types**: Standard, Deluxe, Suite, Premium, Presidential
- **Pricing**: Flexible per-night rates
- **Capacity**: Guest limits per room
- **Amenities**: Detailed descriptions
- **Status**: Active/inactive rooms

### Booking System
- **Guest Information**: Name, email, phone
- **Date Management**: Check-in/out with validation
- **Payment Tracking**: Paid/pending status
- **Special Requests**: Custom notes
- **Cancellation**: Booking cancellation with timestamps

### Check-in/Check-out
- **Today's Schedule**: View arrivals and departures
- **Status Tracking**: Real-time guest status
- **Notes System**: Add operational notes
- **Current Guests**: Live guest registry

### Dashboard Analytics
- **Occupancy Rates**: Real-time room utilization
- **Revenue Tracking**: Daily, weekly, monthly
- **Booking Statistics**: Confirmed, cancelled, pending
- **Guest Metrics**: Current occupancy, turnover

## 🔒 Security Features

- **Password Hashing**: Secure password storage
- **Session Management**: User authentication
- **Role-based Access**: Admin vs owner permissions
- **Input Validation**: Form and data validation
- **SQL Injection Protection**: Parameterized queries

## 📊 Reporting & Analytics

### Admin Reports
- System-wide hotel performance
- Total revenue across all properties
- Hotel comparison metrics
- Growth statistics

### Owner Reports
- Hotel-specific analytics
- Room performance metrics
- Revenue trends
- Guest statistics

## 🔧 Customization

### Adding New Room Types
Edit the room type options in `templates/add_room.html`:
```html
<option value="Custom Type">Custom Type</option>
```

### Modifying Dashboard Metrics
Update the dashboard queries in the respective route functions in `multi_hotel_app.py`.

### Styling Changes
Modify `static/css/style.css` for custom styling and branding.

## 🚀 Production Deployment

### Security Checklist
- [ ] Change default admin password
- [ ] Set strong SECRET_KEY
- [ ] Use HTTPS in production
- [ ] Configure proper database backups
- [ ] Set up monitoring and logging
- [ ] Implement rate limiting

### Recommended Setup
- **Web Server**: Nginx + Gunicorn
- **Database**: PostgreSQL (for production)
- **SSL**: Let's Encrypt
- **Monitoring**: Application logs and metrics

## 🤝 Support & Maintenance

### Regular Tasks
- Database backups
- User account management
- System updates
- Performance monitoring

### Troubleshooting
- Check application logs
- Verify database connectivity
- Confirm user permissions
- Review configuration settings

## 📈 Future Enhancements

### Planned Features
- **Multi-language Support**: Internationalization
- **Advanced Reporting**: Custom report builder
- **Mobile App**: Native mobile applications
- **Payment Integration**: Online payment processing
- **Email Notifications**: Automated guest communications
- **Calendar Integration**: Booking calendar views
- **Inventory Management**: Housekeeping and maintenance
- **Customer Portal**: Guest self-service portal

### Integration Possibilities
- **PMS Systems**: Property Management System integration
- **Accounting Software**: Financial system integration
- **Channel Managers**: Online booking platform connections
- **CRM Systems**: Customer relationship management
- **Analytics Platforms**: Advanced business intelligence

## 📞 Technical Support

For technical issues or questions:
1. Check the application logs
2. Review the database for data integrity
3. Verify user permissions and roles
4. Ensure all dependencies are installed
5. Check network connectivity and ports

## 📄 License

This project is provided as-is for educational and commercial use. Modify and distribute according to your needs.

---

**Built with ❤️ for the hospitality industry**

*Empowering hotel owners with modern technology while providing system administrators with centralized control and oversight.*