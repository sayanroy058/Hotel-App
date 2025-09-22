# Hotel Management Dashboard

A modern, responsive hotel management dashboard built with HTML, CSS, and JavaScript. This frontend-only solution provides a comprehensive view of hotel operations with realistic mock data.

## Features

### 📊 Dashboard Overview
- **Room Statistics**: Real-time display of occupied and vacant rooms with occupancy percentages
- **Revenue Tracking**: Weekly and monthly revenue statistics with growth indicators
- **Real-time Clock**: Live date and time display
- **Additional Statistics**: Today's check-ins/check-outs, average stay duration, and total rooms

### 👥 Guest Management
- **Complete Guest List**: Detailed table showing all current guests
- **Guest Information**: Name, mobile number, address, room number, check-in/out times
- **Room Types**: Standard, Deluxe, and Suite classifications
- **Guest Status**: Real-time status tracking (Checked-in, Checking-out)

### 🔍 Interactive Features
- **Search Functionality**: Search guests by name, mobile, room number, or address
- **Filter Options**: Filter guests by room type
- **Guest Details Modal**: Click "View" to see detailed guest information
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices

### 🎨 Modern UI/UX
- **Glass Morphism Design**: Modern frosted glass effect with backdrop blur
- **Gradient Backgrounds**: Beautiful purple-blue gradient theme
- **Smooth Animations**: Hover effects, transitions, and loading animations
- **Color-coded Status**: Visual indicators for different room and guest statuses

## File Structure

```
Hotel/
├── index.html          # Main HTML structure
├── styles.css          # CSS styling and responsive design
├── script.js           # JavaScript functionality and mock data
└── README.md          # This file
```

## Getting Started

1. **Open the Dashboard**: Simply open `index.html` in any modern web browser
2. **No Server Required**: This is a completely frontend solution with no backend dependencies
3. **Mock Data**: The dashboard automatically generates realistic guest data on load

## Usage Guide

### Navigation
- **Search**: Use Ctrl+F or click the search box to find specific guests
- **Filter**: Use the dropdown to filter guests by room type
- **View Details**: Click "View" next to any guest to see detailed information
- **Real-time Updates**: The dashboard updates time every second and occasionally simulates guest status changes

### Data Export (Available Functions)
- **Export CSV**: Use `exportGuestData()` function in browser console
- **Print Report**: Use `printReport()` function or Ctrl+P

## Technical Details

### Technologies Used
- **HTML5**: Semantic structure with accessibility features
- **CSS3**: Modern styling with Flexbox, Grid, and CSS animations
- **Vanilla JavaScript**: ES6+ features with class-based architecture
- **Font Awesome**: Icons for enhanced visual appeal

### Browser Compatibility
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

### Responsive Breakpoints
- **Desktop**: 1024px and above
- **Tablet**: 768px - 1023px
- **Mobile**: 320px - 767px

## Features in Detail

### Mock Data Generation
- **Realistic Names**: Uses common first and last names
- **Valid Addresses**: Generates addresses from major US cities
- **Phone Numbers**: Proper US phone number format
- **Dates**: Realistic check-in/out dates within reasonable ranges
- **Room Assignment**: Prevents duplicate room assignments
- **Financial Calculations**: Accurate pricing based on room type and duration

### Real-time Simulation
- **Live Clock**: Updates every second
- **Status Changes**: Simulates guest status updates every 30 seconds
- **Dynamic Statistics**: All numbers update based on current guest data

### Accessibility Features
- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Friendly**: Proper ARIA labels and semantic HTML
- **High Contrast**: Good color contrast ratios
- **Responsive Text**: Scales appropriately on different screen sizes

## Customization

### Changing Hotel Capacity
```javascript
// In script.js, modify the totalRooms property
this.totalRooms = 150; // Change to your hotel's room count
```

### Adding New Room Types
```javascript
// In generateMockGuests() method
const roomTypes = ['Standard', 'Deluxe', 'Suite', 'Presidential'];
```

### Modifying Room Rates
```javascript
// In calculateRoomRate() method
const rates = {
    'Standard': 120,
    'Deluxe': 180,
    'Suite': 300,
    'Presidential': 500
};
```

## Performance
- **Fast Loading**: Minimal dependencies, loads instantly
- **Smooth Animations**: Optimized CSS transitions
- **Efficient Rendering**: Smart DOM updates for table filtering
- **Memory Efficient**: Proper cleanup and event management

## Future Enhancements

This dashboard could be extended with:
- Backend integration for real data
- User authentication and roles
- Room availability calendar
- Booking management
- Payment processing
- Reporting and analytics
- Email notifications
- Multi-language support

## Support

For questions or issues:
1. Check the browser console for any errors
2. Ensure JavaScript is enabled
3. Use a modern, supported browser
4. Clear browser cache if experiencing issues

---

**Note**: This is a demonstration dashboard with mock data. In a production environment, you would integrate with a real hotel management system and database.
