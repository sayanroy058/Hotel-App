// Hotel Dashboard JavaScript

class HotelDashboard {
    constructor() {
        this.totalRooms = 100;
        this.guests = this.generateMockGuests();
        this.init();
    }

    init() {
        this.updateDateTime();
        this.renderDashboard();
        this.setupEventListeners();
        this.startRealTimeUpdates();
    }

    generateMockGuests() {
        const firstNames = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Robert', 'Lisa', 
            'William', 'Jennifer', 'James', 'Maria', 'Christopher', 'Anna', 'Daniel', 
            'Patricia', 'Matthew', 'Michelle', 'Anthony', 'Linda', 'Mark', 'Elizabeth',
            'Steven', 'Susan', 'Paul', 'Jessica', 'Andrew', 'Karen', 'Joshua', 'Nancy'
        ];

        const lastNames = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 
            'Ramirez', 'Lewis', 'Robinson'
        ];

        const cities = [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
            'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville',
            'Fort Worth', 'Columbus', 'Charlotte', 'San Francisco', 'Indianapolis',
            'Seattle', 'Denver', 'Washington', 'Boston', 'El Paso', 'Detroit', 
            'Nashville', 'Portland', 'Memphis', 'Oklahoma City', 'Las Vegas'
        ];

        const states = [
            'CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI', 
            'NJ', 'VA', 'WA', 'AZ', 'MA', 'TN', 'IN', 'MO', 'MD', 'WI'
        ];

        const roomTypes = ['Standard', 'Deluxe', 'Suite'];
        const bookingSources = ['Offline', 'OYO', 'MakeMyTrip', 'Goibibo', 'Booking.com', 'Expedia', 'Agoda'];
        const guests = [];

        // Generate 45-65 current guests for realistic occupancy
        const guestCount = Math.floor(Math.random() * 21) + 45;
        const occupiedRooms = new Set();

        for (let i = 0; i < guestCount; i++) {
            let roomNumber;
            do {
                roomNumber = Math.floor(Math.random() * 100) + 1;
            } while (occupiedRooms.has(roomNumber));
            
            occupiedRooms.add(roomNumber);

            const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
            const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
            const city = cities[Math.floor(Math.random() * cities.length)];
            const state = states[Math.floor(Math.random() * states.length)];
            const roomType = roomTypes[Math.floor(Math.random() * roomTypes.length)];

            // Generate realistic check-in dates (within last 7 days)
            const checkInDate = new Date();
            checkInDate.setDate(checkInDate.getDate() - Math.floor(Math.random() * 7));
            
            // Generate check-out dates (1-5 days from check-in)
            const checkOutDate = new Date(checkInDate);
            checkOutDate.setDate(checkOutDate.getDate() + Math.floor(Math.random() * 5) + 1);

            // Generate random phone number
            const phoneNumber = `+1 (${Math.floor(Math.random() * 900) + 100}) ${Math.floor(Math.random() * 900) + 100}-${Math.floor(Math.random() * 9000) + 1000}`;

            const bookingSource = bookingSources[Math.floor(Math.random() * bookingSources.length)];
            const guest = {
                id: i + 1,
                name: `${firstName} ${lastName}`,
                mobile: phoneNumber,
                address: `${Math.floor(Math.random() * 9999) + 1} Main St, ${city}, ${state}`,
                roomNumber: roomNumber,
                roomType: roomType,
                checkIn: checkInDate,
                checkOut: checkOutDate,
                status: Math.random() > 0.1 ? 'checked-in' : 'checking-out',
                email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@email.com`,
                idNumber: `ID${Math.floor(Math.random() * 900000) + 100000}`,
                totalAmount: this.calculateRoomRate(roomType) * this.calculateStayDuration(checkInDate, checkOutDate),
                bookingSource: bookingSource,
                bookingDate: new Date(checkInDate.getTime() - Math.floor(Math.random() * 14) * 24 * 60 * 60 * 1000) // Booked 1-14 days before check-in
            };

            guests.push(guest);
        }

        return guests;
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

        document.getElementById('current-date').textContent = now.toLocaleDateString('en-US', dateOptions);
        document.getElementById('current-time').textContent = now.toLocaleTimeString('en-US', timeOptions);
    }

    renderDashboard() {
        this.updateRoomStats();
        this.updateRevenueStats();
        this.renderGuestTable();
        this.updateAdditionalStats();
    }

    updateRoomStats() {
        const occupiedRooms = this.guests.length;
        const vacantRooms = this.totalRooms - occupiedRooms;
        const occupancyRate = Math.round((occupiedRooms / this.totalRooms) * 100);
        const vacancyRate = 100 - occupancyRate;

        document.getElementById('occupied-rooms').textContent = occupiedRooms;
        document.getElementById('vacant-rooms').textContent = vacantRooms;
        document.getElementById('occupancy-rate').textContent = `${occupancyRate}%`;
        document.getElementById('vacancy-rate').textContent = `${vacancyRate}%`;
    }

    updateRevenueStats() {
        const weeklyRevenue = this.calculateWeeklyRevenue();
        const monthlyRevenue = this.calculateMonthlyRevenue();

        document.getElementById('weekly-revenue').textContent = `₹${weeklyRevenue.toLocaleString()}`;
        document.getElementById('monthly-revenue').textContent = `₹${monthlyRevenue.toLocaleString()}`;
    }

    calculateWeeklyRevenue() {
        const weekAgo = new Date();
        weekAgo.setDate(weekAgo.getDate() - 7);

        let revenue = 0;
        this.guests.forEach(guest => {
            if (guest.checkIn >= weekAgo) {
                revenue += guest.totalAmount;
            }
        });

        return revenue + Math.floor(Math.random() * 5000) + 15000; // Add some base revenue
    }

    calculateMonthlyRevenue() {
        const monthAgo = new Date();
        monthAgo.setMonth(monthAgo.getMonth() - 1);

        let revenue = 0;
        this.guests.forEach(guest => {
            revenue += guest.totalAmount;
        });

        return revenue * 4 + Math.floor(Math.random() * 10000) + 45000; // Extrapolate monthly
    }

    renderGuestTable() {
        const tableBody = document.getElementById('guests-table-body');
        tableBody.innerHTML = '';

        this.guests.forEach(guest => {
            const row = this.createGuestRow(guest);
            tableBody.appendChild(row);
        });

        // Add fade-in animation
        setTimeout(() => {
            tableBody.classList.add('fade-in-up');
        }, 100);
    }

    createGuestRow(guest) {
        const row = document.createElement('tr');
        const duration = this.calculateStayDuration(guest.checkIn, guest.checkOut);
        
        row.innerHTML = `
            <td><strong>${guest.roomNumber}</strong></td>
            <td>${guest.name}</td>
            <td>${guest.mobile}</td>
            <td>${guest.address}</td>
            <td>${guest.checkIn.toLocaleDateString()} ${guest.checkIn.toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'})}</td>
            <td>${guest.checkOut.toLocaleDateString()} ${guest.checkOut.toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'})}</td>
            <td>${duration} day${duration > 1 ? 's' : ''}</td>
            <td>${guest.roomType}</td>
            <td><span class="status-badge ${guest.status.replace('-', '-')}">${guest.status.replace('-', ' ').toUpperCase()}</span></td>
            <td>
                <button class="action-btn view" onclick="dashboard.showGuestDetails(${guest.id})">View</button>
                <button class="action-btn edit" onclick="dashboard.editGuest(${guest.id})">Edit</button>
            </td>
        `;

        return row;
    }

    updateAdditionalStats() {
        const today = new Date();
        const todayCheckins = this.guests.filter(guest => 
            guest.checkIn.toDateString() === today.toDateString()
        ).length;

        const todayCheckouts = this.guests.filter(guest => 
            guest.checkOut.toDateString() === today.toDateString()
        ).length;

        const avgStay = this.guests.reduce((sum, guest) => 
            sum + this.calculateStayDuration(guest.checkIn, guest.checkOut), 0
        ) / this.guests.length;

        document.getElementById('today-checkins').textContent = todayCheckins;
        document.getElementById('today-checkouts').textContent = todayCheckouts;
        document.getElementById('avg-stay').textContent = `${Math.round(avgStay * 10) / 10} days`;
        document.getElementById('total-rooms').textContent = this.totalRooms;
    }

    setupEventListeners() {
        // Search functionality
        const searchInput = document.getElementById('search-guests');
        searchInput.addEventListener('input', (e) => {
            this.filterGuests(e.target.value);
        });

        // Room filter
        const roomFilter = document.getElementById('room-filter');
        roomFilter.addEventListener('change', (e) => {
            this.filterGuestsByRoom(e.target.value);
        });

        // Modal close functionality
        const modal = document.getElementById('guest-modal');
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

    filterGuests(searchTerm) {
        const filteredGuests = this.guests.filter(guest =>
            guest.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            guest.mobile.includes(searchTerm) ||
            guest.roomNumber.toString().includes(searchTerm) ||
            guest.address.toLowerCase().includes(searchTerm.toLowerCase())
        );

        this.renderFilteredGuests(filteredGuests);
    }

    filterGuestsByRoom(roomType) {
        const filteredGuests = roomType ? 
            this.guests.filter(guest => guest.roomType === roomType) : 
            this.guests;

        this.renderFilteredGuests(filteredGuests);
    }

    renderFilteredGuests(filteredGuests) {
        const tableBody = document.getElementById('guests-table-body');
        tableBody.innerHTML = '';

        filteredGuests.forEach(guest => {
            const row = this.createGuestRow(guest);
            tableBody.appendChild(row);
        });
    }

    showGuestDetails(guestId) {
        const guest = this.guests.find(g => g.id === guestId);
        if (!guest) return;

        const modal = document.getElementById('guest-modal');
        const modalBody = document.getElementById('modal-body');
        
        const duration = this.calculateStayDuration(guest.checkIn, guest.checkOut);
        
        modalBody.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div>
                    <h4 style="color: #3498db; margin-bottom: 10px;">Personal Information</h4>
                    <p><strong>Name:</strong> ${guest.name}</p>
                    <p><strong>Mobile:</strong> ${guest.mobile}</p>
                    <p><strong>Email:</strong> ${guest.email}</p>
                    <p><strong>ID Number:</strong> ${guest.idNumber}</p>
                    <p><strong>Address:</strong> ${guest.address}</p>
                </div>
                <div>
                    <h4 style="color: #3498db; margin-bottom: 10px;">Booking Details</h4>
                    <p><strong>Room Number:</strong> ${guest.roomNumber}</p>
                    <p><strong>Room Type:</strong> ${guest.roomType}</p>
                    <p><strong>Check-in:</strong> ${guest.checkIn.toLocaleDateString()} ${guest.checkIn.toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'})}</p>
                    <p><strong>Check-out:</strong> ${guest.checkOut.toLocaleDateString()} ${guest.checkOut.toLocaleTimeString('en-US', {hour: '2-digit', minute: '2-digit'})}</p>
                    <p><strong>Duration:</strong> ${duration} day${duration > 1 ? 's' : ''}</p>
                </div>
            </div>
            <div style="border-top: 1px solid #ecf0f1; padding-top: 20px;">
                <h4 style="color: #3498db; margin-bottom: 10px;">Financial Information</h4>
                <p><strong>Room Rate:</strong> ₹${this.calculateRoomRate(guest.roomType)} per night</p>
                <p><strong>Total Amount:</strong> ₹${guest.totalAmount.toLocaleString()}</p>
                <p><strong>Status:</strong> <span class="status-badge ${guest.status.replace('-', '-')}">${guest.status.replace('-', ' ').toUpperCase()}</span></p>
            </div>
        `;

        modal.style.display = 'block';
    }

    editGuest(guestId) {
        // In a real application, this would open an edit form
        alert(`Edit functionality would open here for guest ID: ${guestId}`);
    }

    startRealTimeUpdates() {
        // Update time every second
        setInterval(() => {
            this.updateDateTime();
        }, 1000);

        // Simulate occasional guest updates (every 30 seconds)
        setInterval(() => {
            this.simulateGuestUpdate();
        }, 30000);
    }

    simulateGuestUpdate() {
        // Occasionally update guest status or add/remove guests
        if (Math.random() > 0.7) {
            const randomGuest = this.guests[Math.floor(Math.random() * this.guests.length)];
            if (randomGuest.status === 'checked-in') {
                randomGuest.status = 'checking-out';
            }
            
            this.renderDashboard();
        }
    }
}

// Initialize the dashboard when the page loads
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new HotelDashboard();
});

// Additional utility functions
function exportGuestData() {
    const csvContent = dashboard.guests.map(guest => {
        return [
            guest.roomNumber,
            guest.name,
            guest.mobile,
            guest.address,
            guest.checkIn.toISOString(),
            guest.checkOut.toISOString(),
            guest.roomType,
            guest.status,
            guest.totalAmount
        ].join(',');
    }).join('\n');

    const header = 'Room,Name,Mobile,Address,CheckIn,CheckOut,RoomType,Status,TotalAmount\n';
    const blob = new Blob([header + csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hotel_guests_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
}

function printReport() {
    window.print();
}

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        document.getElementById('search-guests').focus();
    }
});
