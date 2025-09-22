// Upcoming Bookings Dashboard JavaScript

class UpcomingBookingsManager {
    constructor() {
        this.allBookings = this.generateUpcomingBookings();
        this.filteredBookings = this.allBookings;
        this.init();
    }

    init() {
        this.updateDateTime();
        this.renderDashboard();
        this.setupEventListeners();
        this.startRealTimeUpdates();
    }

    generateUpcomingBookings() {
        const firstNames = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Robert', 'Lisa', 
            'William', 'Jennifer', 'James', 'Maria', 'Christopher', 'Anna', 'Daniel', 
            'Patricia', 'Matthew', 'Michelle', 'Anthony', 'Linda', 'Mark', 'Elizabeth',
            'Steven', 'Susan', 'Paul', 'Jessica', 'Andrew', 'Karen', 'Joshua', 'Nancy',
            'Kevin', 'Betty', 'Ronald', 'Dorothy', 'Jason', 'Helen', 'Jeffrey', 'Sharon'
        ];

        const lastNames = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 
            'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King'
        ];

        const cities = [
            'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata',
            'Pune', 'Ahmedabad', 'Jaipur', 'Surat', 'Lucknow', 'Kanpur',
            'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Visakhapatnam', 'Pimpri'
        ];

        const states = [
            'MH', 'DL', 'KA', 'TG', 'TN', 'WB', 
            'GJ', 'RJ', 'UP', 'MP', 'AP', 'HR'
        ];

        const roomTypes = ['Standard', 'Deluxe', 'Suite'];
        const bookingSources = ['Offline', 'OYO', 'MakeMyTrip', 'Goibibo', 'Booking.com', 'Expedia', 'Agoda'];
        const bookings = [];

        // Generate 80-120 upcoming bookings over the next 3 months
        const bookingCount = Math.floor(Math.random() * 41) + 80;
        const usedRoomDates = new Set();

        for (let i = 0; i < bookingCount; i++) {
            let roomNumber;
            let checkInDate;
            let roomDateKey;

            // Ensure no room conflicts on the same dates
            do {
                roomNumber = Math.floor(Math.random() * 100) + 1;
                // Generate check-in dates from tomorrow to 90 days in future
                checkInDate = new Date();
                checkInDate.setDate(checkInDate.getDate() + Math.floor(Math.random() * 90) + 1);
                roomDateKey = `${roomNumber}-${checkInDate.toISOString().split('T')[0]}`;
            } while (usedRoomDates.has(roomDateKey));

            usedRoomDates.add(roomDateKey);

            const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
            const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
            const city = cities[Math.floor(Math.random() * cities.length)];
            const state = states[Math.floor(Math.random() * states.length)];
            const roomType = roomTypes[Math.floor(Math.random() * roomTypes.length)];
            const bookingSource = bookingSources[Math.floor(Math.random() * bookingSources.length)];

            // Generate check-out dates (1-7 days from check-in)
            const checkOutDate = new Date(checkInDate);
            checkOutDate.setDate(checkOutDate.getDate() + Math.floor(Math.random() * 7) + 1);

            // Generate booking date (1-45 days before check-in)
            const bookingDate = new Date(checkInDate.getTime() - Math.floor(Math.random() * 45) * 24 * 60 * 60 * 1000);

            // Generate random Indian phone number
            const phoneNumber = `+91 ${Math.floor(Math.random() * 90000) + 10000}-${Math.floor(Math.random() * 90000) + 10000}`;

            const booking = {
                id: i + 1,
                name: `${firstName} ${lastName}`,
                mobile: phoneNumber,
                address: `${Math.floor(Math.random() * 999) + 1} ${city} Road, ${city}, ${state}`,
                roomNumber: roomNumber,
                roomType: roomType,
                checkIn: checkInDate,
                checkOut: checkOutDate,
                bookingSource: bookingSource,
                bookingDate: bookingDate,
                email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@email.com`,
                idNumber: `ID${Math.floor(Math.random() * 900000) + 100000}`,
                totalAmount: this.calculateRoomRate(roomType) * this.calculateStayDuration(checkInDate, checkOutDate),
                status: 'confirmed'
            };

            bookings.push(booking);
        }

        // Sort by check-in date
        return bookings.sort((a, b) => a.checkIn - b.checkIn);
    }

    calculateRoomRate(roomType) {
        const rates = {
            'Standard': 2500,  // ₹2,500 per night
            'Deluxe': 4200,    // ₹4,200 per night
            'Suite': 7500      // ₹7,500 per night
        };
        return rates[roomType] || 2500;
    }

    calculateStayDuration(checkIn, checkOut) {
        const diffTime = Math.abs(checkOut - checkIn);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays || 1;
    }

    updateDateTime() {
        const now = new Date();
        const dateOptions = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        const timeOptions = { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit',
            hour12: true 
        };

        document.getElementById('current-date').textContent = now.toLocaleDateString('en-IN', dateOptions);
        document.getElementById('current-time').textContent = now.toLocaleTimeString('en-IN', timeOptions);
    }

    renderDashboard() {
        this.updateStats();
        this.renderBookingsTable();
        this.updateBookingSourcesAnalytics();
    }

    updateStats() {
        const now = new Date();
        const next7Days = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
        const next30Days = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);

        const bookings7Days = this.allBookings.filter(booking => 
            booking.checkIn >= now && booking.checkIn <= next7Days
        );

        const bookings30Days = this.allBookings.filter(booking => 
            booking.checkIn >= now && booking.checkIn <= next30Days
        );

        const expectedRevenue = bookings30Days.reduce((sum, booking) => sum + booking.totalAmount, 0);

        // Find top booking source
        const sourceCounts = {};
        bookings30Days.forEach(booking => {
            sourceCounts[booking.bookingSource] = (sourceCounts[booking.bookingSource] || 0) + 1;
        });

        let topSource = '-';
        let topSourceCount = 0;
        Object.entries(sourceCounts).forEach(([source, count]) => {
            if (count > topSourceCount) {
                topSourceCount = count;
                topSource = source;
            }
        });

        const topSourcePercentage = bookings30Days.length > 0 ? 
            Math.round((topSourceCount / bookings30Days.length) * 100) : 0;

        document.getElementById('upcoming-7-days').textContent = bookings7Days.length;
        document.getElementById('upcoming-30-days').textContent = bookings30Days.length;
        document.getElementById('expected-revenue').textContent = `₹${expectedRevenue.toLocaleString('en-IN')}`;
        document.getElementById('top-source').textContent = topSource;
        document.getElementById('top-source-percentage').textContent = `${topSourcePercentage}%`;
    }

    renderBookingsTable() {
        const tableBody = document.getElementById('bookings-table-body');
        tableBody.innerHTML = '';

        this.filteredBookings.forEach(booking => {
            const row = this.createBookingRow(booking);
            tableBody.appendChild(row);
        });

        // Add fade-in animation
        setTimeout(() => {
            tableBody.classList.add('fade-in-up');
        }, 100);
    }

    createBookingRow(booking) {
        const row = document.createElement('tr');
        const duration = this.calculateStayDuration(booking.checkIn, booking.checkOut);
        
        row.innerHTML = `
            <td><strong>${booking.checkIn.toLocaleDateString('en-IN')}</strong></td>
            <td>${booking.name}</td>
            <td>${booking.mobile}</td>
            <td>${booking.roomType}</td>
            <td>${duration} day${duration > 1 ? 's' : ''}</td>
            <td><span class="source-badge ${booking.bookingSource.toLowerCase().replace('.', '-')}">${booking.bookingSource}</span></td>
            <td><strong>₹${booking.totalAmount.toLocaleString('en-IN')}</strong></td>
            <td>${booking.bookingDate.toLocaleDateString('en-IN')}</td>
            <td>
                <button class="action-btn view" onclick="upcomingBookings.showBookingDetails(${booking.id})">View</button>
            </td>
        `;

        return row;
    }

    updateBookingSourcesAnalytics() {
        const now = new Date();
        const next30Days = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000);
        
        const bookings30Days = this.allBookings.filter(booking => 
            booking.checkIn >= now && booking.checkIn <= next30Days
        );

        const sourceCounts = {};
        const sourceRevenue = {};
        
        bookings30Days.forEach(booking => {
            sourceCounts[booking.bookingSource] = (sourceCounts[booking.bookingSource] || 0) + 1;
            sourceRevenue[booking.bookingSource] = (sourceRevenue[booking.bookingSource] || 0) + booking.totalAmount;
        });

        const sourcesContainer = document.getElementById('booking-sources');
        sourcesContainer.innerHTML = '';

        Object.entries(sourceCounts).forEach(([source, count]) => {
            const percentage = bookings30Days.length > 0 ? 
                Math.round((count / bookings30Days.length) * 100) : 0;
            const revenue = sourceRevenue[source] || 0;

            const sourceCard = document.createElement('div');
            sourceCard.className = 'source-stat-card';
            sourceCard.innerHTML = `
                <div class="source-header">
                    <h4>${source}</h4>
                    <span class="source-badge ${source.toLowerCase().replace('.', '-')}">${source}</span>
                </div>
                <div class="source-stats">
                    <div class="source-count">${count} bookings</div>
                    <div class="source-percentage">${percentage}%</div>
                    <div class="source-revenue">₹${revenue.toLocaleString('en-IN')}</div>
                </div>
            `;

            sourcesContainer.appendChild(sourceCard);
        });
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('search-bookings');
        searchInput.addEventListener('input', (e) => {
            this.filterBookings();
        });

        // Time filter
        const timeFilter = document.getElementById('time-filter');
        timeFilter.addEventListener('change', (e) => {
            this.filterBookings();
        });

        // Source filter
        const sourceFilter = document.getElementById('source-filter');
        sourceFilter.addEventListener('change', (e) => {
            this.filterBookings();
        });

        // Modal close functionality
        const modal = document.getElementById('booking-modal');
        const closeBtn = document.querySelector('.close');
        
        closeBtn.onclick = () => {
            modal.style.display = 'none';
        };

        window.onclick = (event) => {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        };
    }

    filterBookings() {
        const searchTerm = document.getElementById('search-bookings').value.toLowerCase();
        const timeFilter = document.getElementById('time-filter').value;
        const sourceFilter = document.getElementById('source-filter').value;

        let filtered = this.allBookings;

        // Apply search filter
        if (searchTerm) {
            filtered = filtered.filter(booking =>
                booking.name.toLowerCase().includes(searchTerm) ||
                booking.mobile.includes(searchTerm) ||
                booking.roomNumber.toString().includes(searchTerm) ||
                booking.bookingSource.toLowerCase().includes(searchTerm)
            );
        }

        // Apply time filter
        if (timeFilter && timeFilter !== 'all') {
            const now = new Date();
            const filterDate = new Date(now.getTime() + parseInt(timeFilter) * 24 * 60 * 60 * 1000);
            filtered = filtered.filter(booking => 
                booking.checkIn >= now && booking.checkIn <= filterDate
            );
        }

        // Apply source filter
        if (sourceFilter) {
            filtered = filtered.filter(booking => booking.bookingSource === sourceFilter);
        }

        this.filteredBookings = filtered;
        this.renderBookingsTable();
    }

    showBookingDetails(bookingId) {
        const booking = this.allBookings.find(b => b.id === bookingId);
        if (!booking) return;

        const modal = document.getElementById('booking-modal');
        const modalBody = document.getElementById('modal-body');
        
        const duration = this.calculateStayDuration(booking.checkIn, booking.checkOut);
        
        modalBody.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div>
                    <h4 style="color: #3498db; margin-bottom: 10px;">Personal Information</h4>
                    <p><strong>Name:</strong> ${booking.name}</p>
                    <p><strong>Mobile:</strong> ${booking.mobile}</p>
                    <p><strong>Email:</strong> ${booking.email}</p>
                    <p><strong>ID Number:</strong> ${booking.idNumber}</p>
                    <p><strong>Address:</strong> ${booking.address}</p>
                </div>
                <div>
                    <h4 style="color: #3498db; margin-bottom: 10px;">Booking Details</h4>
                    <p><strong>Room Number:</strong> ${booking.roomNumber}</p>
                    <p><strong>Room Type:</strong> ${booking.roomType}</p>
                    <p><strong>Check-in:</strong> ${booking.checkIn.toLocaleDateString('en-IN')} ${booking.checkIn.toLocaleTimeString('en-IN', {hour: '2-digit', minute: '2-digit'})}</p>
                    <p><strong>Check-out:</strong> ${booking.checkOut.toLocaleDateString('en-IN')} ${booking.checkOut.toLocaleTimeString('en-IN', {hour: '2-digit', minute: '2-digit'})}</p>
                    <p><strong>Duration:</strong> ${duration} day${duration > 1 ? 's' : ''}</p>
                </div>
            </div>
            <div style="border-top: 1px solid #ecf0f1; padding-top: 20px;">
                <h4 style="color: #3498db; margin-bottom: 10px;">Booking Information</h4>
                <p><strong>Booking Source:</strong> <span class="source-badge ${booking.bookingSource.toLowerCase().replace('.', '-')}">${booking.bookingSource}</span></p>
                <p><strong>Booking Date:</strong> ${booking.bookingDate.toLocaleDateString('en-IN')}</p>
                <p><strong>Room Rate:</strong> ₹${this.calculateRoomRate(booking.roomType).toLocaleString('en-IN')} per night</p>
                <p><strong>Total Amount:</strong> <strong>₹${booking.totalAmount.toLocaleString('en-IN')}</strong></p>
                <p><strong>Status:</strong> <span class="status-badge confirmed">CONFIRMED</span></p>
            </div>
        `;

        modal.style.display = 'block';
    }

    startRealTimeUpdates() {
        // Update time every second
        setInterval(() => {
            this.updateDateTime();
        }, 1000);
    }
}

// Initialize the dashboard when the page loads
let upcomingBookings;
document.addEventListener('DOMContentLoaded', () => {
    upcomingBookings = new UpcomingBookingsManager();
});
