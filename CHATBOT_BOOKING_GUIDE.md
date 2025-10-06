# Conversational Booking Chatbot - User Guide

## Overview
The hotel management system now includes an intelligent conversational chatbot that guides users through the booking process step-by-step, eliminating the need for complex AI calls for standard booking workflows.

## Features Implemented

### 1. **Conversational Booking Flow**
The chatbot now handles bookings through a guided conversation without AI intervention:

#### Steps:
1. **Initiate Booking**: Type `new booking`, `create booking`, `book room`, or `make booking`
2. **Guest Name**: The chatbot asks for the guest's name
3. **Check-in Date**: Enter check-in date in YYYY-MM-DD format (e.g., 2025-10-15)
4. **Check-out Date**: Enter check-out date in YYYY-MM-DD format
5. **Number of Guests**: Specify how many guests will be staying
6. **Room Selection**: The chatbot displays available rooms with:
   - Room number
   - Room type
   - Price per night
   - Capacity
   - Only shows rooms available for the selected dates
7. **Payment Status**: Confirm if payment is `paid` or `pending`
8. **Booking Confirmation**: The system creates the booking and provides:
   - Booking ID
   - Complete booking summary
   - Payment status
   - Note about marking payment from bookings page if pending

### 2. **Quick Commands**
- **View Bookings**: Type `check bookings`, `view bookings`, or `booking list`
  - Shows recent bookings with guest name, room number, check-in date, and status
  
- **Check Room Availability**: Type `check rooms`, `available rooms`, or `room availability`
  - Displays all active rooms with numbers, types, and prices

### 3. **Data Validation**
The chatbot includes comprehensive validation:
- ✅ Check-in date cannot be in the past
- ✅ Check-out date must be after check-in date
- ✅ Number of guests must be at least 1
- ✅ Room selection validated against available rooms
- ✅ Date format validation (YYYY-MM-DD)
- ✅ Room availability checked for selected dates

### 4. **Smart Room Availability**
- Automatically filters out rooms already booked for overlapping dates
- Displays only rooms that match capacity requirements
- Shows real-time pricing information

### 5. **Booking Summary**
After completing the booking, users receive:
```
🎉 Booking Created Successfully!

📋 Booking ID: #123
• Guest: John Doe
• Room: 101 - Deluxe Room
• Check-in: 2025-10-15
• Check-out: 2025-10-17
• Guests: 2
• Total: ₹5000
• Status: ✅ Payment Received (or ⏳ Payment Pending)
```

### 6. **Mark as Paid Functionality**
Owners can update payment status from the bookings page:
- Navigate to **Owner Dashboard → Bookings**
- Find bookings with "Pending" payment status
- Click the **💰 Mark as Paid** button
- Confirmation dialog appears
- Payment status updates immediately
- Page refreshes to show updated status

## Technical Details

### Database Schema
```sql
INSERT INTO bookings (
    hotel_id, room_id, guest_name, guest_email, guest_phone, 
    check_in_date, check_out_date, guest_count, 
    total_amount, booking_status, payment_status, created_at
)
```

### Session State Management
The chatbot uses Flask sessions to maintain conversation state:
- `flow`: Current conversation flow (e.g., 'booking')
- `step`: Current step in the flow (e.g., 'name', 'check_in', 'check_out', etc.)
- `data`: Accumulated booking data throughout the conversation

### API Endpoints

#### Chatbot Response
- **Route**: `/owner/chatbot`
- **Method**: POST
- **Request**: `{ "message": "user message" }`
- **Response**: `{ "response": "chatbot response", "show_input": true }`

#### Mark as Paid
- **Route**: `/owner/bookings/<booking_id>/mark-paid`
- **Method**: POST
- **Response**: `{ "success": true }` or `{ "success": false, "error": "..." }`

## User Interface Enhancements

### Quick Action Buttons
The owner dashboard now includes three quick action buttons:
1. **📝 New Booking** - Starts the conversational booking flow
2. **📋 View Bookings** - Shows recent bookings list
3. **🔍 Check Availability** - Displays available rooms

### Chat Interface
- Modern chat bubble design
- Real-time message updates
- User messages aligned right (blue)
- Bot messages aligned left (gray)
- Auto-scroll to latest message
- Enter key support for sending messages

### Enhanced Styling
- Gradient backgrounds for cards and navigation
- Smooth animations (fadeIn, slideIn effects)
- Responsive design for mobile and desktop
- Hover effects on interactive elements
- Modern color scheme with CSS variables

## Usage Examples

### Example 1: Creating a Booking
```
Owner: new booking
Bot: 🏨 Great! Let's create a new booking. Please provide the guest's name:

Owner: John Doe
Bot: ✅ Guest Name: John Doe. Please provide the check-in date (YYYY-MM-DD):

Owner: 2025-10-15
Bot: ✅ Check-in: 2025-10-15. Please provide the check-out date (YYYY-MM-DD):

Owner: 2025-10-17
Bot: ✅ Check-out: 2025-10-17. How many guests will be staying?

Owner: 2
Bot: ✅ Number of guests: 2
     🛏️ Available rooms for your dates:
     1. Room 101 - Deluxe Room
        Price: ₹2500/night
        Capacity: 2 guests
     Please type the room number you want to book:

Owner: 101
Bot: ✅ Room Selected: 101 - Deluxe Room
     📋 Booking Summary:
     • Total: ₹5000
     💳 Has the payment been received? Type "paid" or "pending":

Owner: paid
Bot: 🎉 Booking Created Successfully! [Full summary displayed]
```

### Example 2: Checking Bookings
```
Owner: check bookings
Bot: 📋 Recent Bookings:
     • John Doe - Room 101
       Check-in: 2025-10-15 | Status: confirmed
```

### Example 3: Marking Payment as Paid
1. Go to Owner Dashboard
2. Click "Bookings" in navigation
3. Find booking with "Pending" payment status
4. Click "💰 Mark as Paid" button
5. Confirm in dialog
6. Status updates to "Paid"

## Error Handling
The chatbot gracefully handles errors:
- Invalid date formats
- Past check-in dates
- Check-out before check-in
- Invalid room selections
- Database errors
- No room availability

All errors provide clear feedback and allow users to retry without losing progress.

## Benefits
1. **No AI Dependency**: Standard bookings don't require AI processing
2. **Faster Response**: Instant replies without API calls
3. **Guided Process**: Step-by-step workflow reduces errors
4. **Data Validation**: Built-in checks ensure data quality
5. **User-Friendly**: Natural conversation flow
6. **Cost-Effective**: Reduces AI API costs
7. **Reliable**: Deterministic behavior for common tasks

## Future Enhancements
Potential improvements:
- Email and phone number collection during booking
- Special requests/notes field
- Multi-room booking support
- Guest history lookup
- Discount code application
- Automated email confirmations
- Calendar integration

---

**Version**: 1.0  
**Last Updated**: 2025  
**Status**: ✅ Fully Functional
