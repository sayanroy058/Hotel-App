// All Bookings Manager JavaScript

class AllBookingsManager {
    constructor() {
        this.allBookings = this.generateAllBookings();
        this.filteredBookings = this.allBookings;
        this.currentPage = 1;
        this.itemsPerPage = 50;
        this.init();
    }

    init() {
        this.updateDateTime();
        this.renderDashboard();
        this.setupEventListeners();
        this.startRealTimeUpdates();
    }

    generateAllBookings() {
        const firstNames = [
            'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emma', 'Robert', 'Lisa', 
            'William', 'Jennifer', 'James', 'Maria', 'Christopher', 'Anna', 'Daniel', 
            'Patricia', 'Matthew', 'Michelle', 'Anthony', 'Linda', 'Mark', 'Elizabeth',
            'Steven', 'Susan', 'Paul', 'Jessica', 'Andrew', 'Karen', 'Joshua', 'Nancy',
            'Kevin', 'Betty', 'Ronald', 'Dorothy', 'Jason', 'Helen', 'Jeffrey', 'Sharon',
            'Brian', 'Amy', 'Edward', 'Angela', 'Ralph', 'Brenda', 'Roy', 'Emma',
            'Eugene', 'Olivia', 'Wayne', 'Cynthia', 'Louis', 'Marie', 'Philip', 'Janet'
        ];

        const lastNames = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
            'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
            'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 
            'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King',
            'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green'
        ];

        const cities = [
            'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata',
            'Pune', 'Ahmedabad', 'Jaipur', 'Surat', 'Lucknow', 'Kanpur',
            'Nagpur', 'Indore', 'Thane', 'Bhopal', 'Visakhapatnam', 'Pimpri',
            'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana', 'Coimbatore', 'Madurai'
        ];

        const states = [
            'MH', 'DL', 'KA', 'TG', 'TN', 'WB', 'GJ', 'RJ', 'UP', 'MP', 
            'AP', 'HR', 'BR', 'PB', 'OR', 'KL', 'AS', 'JH', 'UK', 'HP'
        ];

        const roomTypes = ['Standard', 'Deluxe', 'Suite'];
        const bookingSources = ['Offline', 'OYO', 'MakeMyTrip', 'Goibibo', 'Booking.com', 'Expedia', 'Agoda'];
        const bookingStatuses = ['confirmed', 'checked-in', 'completed', 'cancelled'];
        const bookings = [];

        // Generate 300-500 bookings over the past 12 months and future 3 months
        const bookingCount = Math.floor(Math.random() * 201) + 300;

        for (let i = 0; i < bookingCount; i++) {
            const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
            const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
            const city = cities[Math.floor(Math.random() * cities.length)];
            const state = states[Math.floor(Math.random() * states.length)];
            const roomType = roomTypes[Math.floor(Math.random() * roomTypes.length)];
            const bookingSource = bookingSources[Math.floor(Math.random() * bookingSources.length)];

            // Generate booking dates from 12 months ago to 3 months in future
            const bookingDate = new Date();
            const daysOffset = Math.floor(Math.random() * 450) - 365; // -365 to +85 days
            bookingDate.setDate(bookingDate.getDate() + daysOffset);

            // Generate check-in dates (0-60 days after booking)
            const checkInDate = new Date(bookingDate);
            checkInDate.setDate(checkInDate.getDate() + Math.floor(Math.random() * 61));

            // Generate check-out dates (1-10 days from check-in)
            const checkOutDate = new Date(checkInDate);
            checkOutDate.setDate(checkOutDate.getDate() + Math.floor(Math.random() * 10) + 1);

            // Determine status based on dates
            const now = new Date();
            let status;
            if (checkOutDate < now) {
                status = Math.random() > 0.1 ? 'completed' : 'cancelled';
            } else if (checkInDate < now && checkOutDate >= now) {
                status = 'checked-in';
            } else {
                status = Math.random() > 0.05 ? 'confirmed' : 'cancelled';
            }

            // Generate random Indian phone number
            const phoneNumber = `+91 ${Math.floor(Math.random() * 90000) + 10000}-${Math.floor(Math.random() * 90000) + 10000}`;

            const roomNumber = Math.floor(Math.random() * 100) + 1;

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
                status: status
            };

            bookings.push(booking);
        }

        // Sort by booking date (newest first)
        return bookings.sort((a, b) => b.bookingDate - a.bookingDate);
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
        this.updateOverviewStats();
        this.applyFiltersAndSort();
        this.updateBookingSourcesAnalytics();
        this.updateMonthlyStats();
        this.updatePagination();
    }

    updateOverviewStats() {
        const totalBookings = this.allBookings.length;
        const totalRevenue = this.allBookings.reduce((sum, booking) => 
            booking.status !== 'cancelled' ? sum + booking.totalAmount : sum, 0);
        const avgBookingValue = totalRevenue / this.allBookings.filter(b => b.status !== 'cancelled').length || 0;
        
        const onlineBookings = this.allBookings.filter(b => b.bookingSource !== 'Offline').length;
        const onlinePercentage = Math.round((onlineBookings / totalBookings) * 100);

        document.getElementById('total-bookings').textContent = totalBookings.toLocaleString('en-IN');
        document.getElementById('total-revenue').textContent = `₹${totalRevenue.toLocaleString('en-IN')}`;
        document.getElementById('avg-booking-value').textContent = `₹${Math.round(avgBookingValue).toLocaleString('en-IN')}`;
        document.getElementById('online-percentage').textContent = `${onlinePercentage}%`;
    }

    applyFiltersAndSort() {
        let filtered = [...this.allBookings];

        // Apply search filter
        const searchTerm = document.getElementById('search-all-bookings').value.toLowerCase();
        if (searchTerm) {
            filtered = filtered.filter(booking =>
                booking.name.toLowerCase().includes(searchTerm) ||
                booking.mobile.includes(searchTerm) ||
                booking.roomNumber.toString().includes(searchTerm) ||
                booking.bookingSource.toLowerCase().includes(searchTerm)
            );
        }

        // Apply source filter
        const sourceFilter = document.getElementById('booking-source-filter').value;
        if (sourceFilter) {
            filtered = filtered.filter(booking => booking.bookingSource === sourceFilter);
        }

        // Apply status filter
        const statusFilter = document.getElementById('booking-status-filter').value;
        if (statusFilter) {
            filtered = filtered.filter(booking => booking.status === statusFilter);
        }

        // Apply room type filter
        const roomTypeFilter = document.getElementById('room-type-filter').value;
        if (roomTypeFilter) {
            filtered = filtered.filter(booking => booking.roomType === roomTypeFilter);
        }

        // Apply date range filter
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        if (startDate && endDate) {
            const start = new Date(startDate);
            const end = new Date(endDate);
            end.setHours(23, 59, 59, 999); // Include entire end date
            filtered = filtered.filter(booking => 
                booking.checkIn >= start && booking.checkIn <= end
            );
        }

        // Apply sorting
        const sortBy = document.getElementById('sort-by').value;
        const [field, direction] = sortBy.split('-');
        
        filtered.sort((a, b) => {
            let aVal, bVal;
            
            switch (field) {
                case 'checkIn':
                case 'bookingDate':
                    aVal = a[field];
                    bVal = b[field];
                    break;
                case 'amount':
                    aVal = a.totalAmount;
                    bVal = b.totalAmount;
                    break;
                case 'name':
                    aVal = a.name.toLowerCase();
                    bVal = b.name.toLowerCase();
                    break;
                default:
                    return 0;
            }

            if (direction === 'asc') {
                return aVal > bVal ? 1 : -1;
            } else {
                return aVal < bVal ? 1 : -1;
            }
        });

        this.filteredBookings = filtered;
        this.currentPage = 1;
        this.renderBookingsTable();
        this.updateResultsInfo();
    }

    renderBookingsTable() {
        const tableBody = document.getElementById('all-bookings-table-body');
        tableBody.innerHTML = '';

        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageBookings = this.filteredBookings.slice(startIndex, endIndex);

        pageBookings.forEach(booking => {
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
        
        // Add row class based on status
        row.className = `booking-row status-${booking.status}`;
        
        row.innerHTML = `
            <td>${booking.bookingDate.toLocaleDateString('en-IN')}</td>
            <td><strong>${booking.name}</strong></td>
            <td>${booking.mobile}</td>
            <td>${booking.checkIn.toLocaleDateString('en-IN')}</td>
            <td>${booking.checkOut.toLocaleDateString('en-IN')}</td>
            <td>${duration} day${duration > 1 ? 's' : ''}</td>
            <td>${booking.roomType}</td>
            <td><span class="source-badge ${booking.bookingSource.toLowerCase().replace('.', '-')}">${booking.bookingSource}</span></td>
            <td><strong>₹${booking.totalAmount.toLocaleString('en-IN')}</strong></td>
            <td><span class="status-badge ${booking.status}">${booking.status.toUpperCase()}</span></td>
            <td>
                <button class="action-btn view" onclick="allBookings.showBookingDetails(${booking.id})">View</button>
                ${booking.status === 'confirmed' ? '<button class="action-btn edit" onclick="allBookings.editBooking(' + booking.id + ')">Edit</button>' : ''}
            </td>
        `;

        return row;
    }

    updateResultsInfo() {
        const showing = Math.min(this.itemsPerPage, this.filteredBookings.length - (this.currentPage - 1) * this.itemsPerPage);
        const start = this.filteredBookings.length > 0 ? (this.currentPage - 1) * this.itemsPerPage + 1 : 0;
        const end = (this.currentPage - 1) * this.itemsPerPage + showing;

        document.getElementById('showing-count').textContent = showing;
        document.getElementById('total-count').textContent = this.filteredBookings.length;
        document.getElementById('pagination-info').textContent = 
            `Showing ${start}-${end} of ${this.filteredBookings.length} results`;
    }

    updatePagination() {
        const totalPages = Math.ceil(this.filteredBookings.length / this.itemsPerPage);
        
        // Update previous/next buttons
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        
        prevBtn.disabled = this.currentPage <= 1;
        nextBtn.disabled = this.currentPage >= totalPages;

        // Update page numbers
        const pageNumbers = document.getElementById('page-numbers');
        pageNumbers.innerHTML = '';

        const maxVisiblePages = 5;
        const startPage = Math.max(1, this.currentPage - Math.floor(maxVisiblePages / 2));
        const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        for (let i = startPage; i <= endPage; i++) {
            const pageBtn = document.createElement('button');
            pageBtn.className = `page-btn ${i === this.currentPage ? 'active' : ''}`;
            pageBtn.textContent = i;
            pageBtn.onclick = () => this.goToPage(i);
            pageNumbers.appendChild(pageBtn);
        }
    }

    goToPage(page) {
        this.currentPage = page;
        this.renderBookingsTable();
        this.updateResultsInfo();
        this.updatePagination();
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.goToPage(this.currentPage - 1);
        }
    }

    nextPage() {
        const totalPages = Math.ceil(this.filteredBookings.length / this.itemsPerPage);
        if (this.currentPage < totalPages) {
            this.goToPage(this.currentPage + 1);
        }
    }

    updateBookingSourcesAnalytics() {
        const sourceCounts = {};
        const sourceRevenue = {};
        
        this.allBookings.forEach(booking => {
            if (booking.status !== 'cancelled') {
                sourceCounts[booking.bookingSource] = (sourceCounts[booking.bookingSource] || 0) + 1;
                sourceRevenue[booking.bookingSource] = (sourceRevenue[booking.bookingSource] || 0) + booking.totalAmount;
            }
        });

        const sourcesContainer = document.getElementById('all-booking-sources');
        sourcesContainer.innerHTML = '';

        Object.entries(sourceCounts).forEach(([source, count]) => {
            const revenue = sourceRevenue[source] || 0;
            const avgBookingValue = revenue / count;

            const sourceCard = document.createElement('div');
            sourceCard.className = 'source-stat-card';
            sourceCard.innerHTML = `
                <div class="source-header">
                    <h4>${source}</h4>
                    <span class="source-badge ${source.toLowerCase().replace('.', '-')}">${source}</span>
                </div>
                <div class="source-stats">
                    <div class="source-count">${count} bookings</div>
                    <div class="source-revenue">₹${revenue.toLocaleString('en-IN')}</div>
                    <div class="source-avg">Avg: ₹${Math.round(avgBookingValue).toLocaleString('en-IN')}</div>
                </div>
            `;

            sourcesContainer.appendChild(sourceCard);
        });
    }

    updateMonthlyStats() {
        const monthlyData = {};
        
        this.allBookings.forEach(booking => {
            if (booking.status !== 'cancelled') {
                const monthKey = `${booking.checkIn.getFullYear()}-${String(booking.checkIn.getMonth() + 1).padStart(2, '0')}`;
                if (!monthlyData[monthKey]) {
                    monthlyData[monthKey] = { bookings: 0, revenue: 0 };
                }
                monthlyData[monthKey].bookings++;
                monthlyData[monthKey].revenue += booking.totalAmount;
            }
        });

        const monthlyContainer = document.getElementById('monthly-stats');
        monthlyContainer.innerHTML = '';
        monthlyContainer.className = 'monthly-stats-grid';

        // Get last 6 months
        const sortedMonths = Object.keys(monthlyData).sort().slice(-6);
        
        sortedMonths.forEach(monthKey => {
            const data = monthlyData[monthKey];
            const [year, month] = monthKey.split('-');
            const monthName = new Date(year, month - 1).toLocaleDateString('en-IN', { month: 'long', year: 'numeric' });

            const monthCard = document.createElement('div');
            monthCard.className = 'monthly-stat-card';
            monthCard.innerHTML = `
                <h5>${monthName}</h5>
                <div class="monthly-bookings">${data.bookings} bookings</div>
                <div class="monthly-revenue">₹${data.revenue.toLocaleString('en-IN')}</div>
            `;

            monthlyContainer.appendChild(monthCard);
        });
    }

    setupEventListeners() {
        // Search functionality
        document.getElementById('search-all-bookings').addEventListener('input', () => {
            this.applyFiltersAndSort();
        });

        // Filter dropdowns
        ['booking-source-filter', 'booking-status-filter', 'room-type-filter', 'sort-by'].forEach(id => {
            document.getElementById(id).addEventListener('change', () => {
                this.applyFiltersAndSort();
            });
        });

        // Quick filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                
                const period = e.target.dataset.period;
                this.applyQuickFilter(period);
            });
        });

        // Modal close functionality
        const modal = document.getElementById('all-booking-modal');
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

    applyQuickFilter(period) {
        const startDateInput = document.getElementById('start-date');
        const endDateInput = document.getElementById('end-date');

        if (period === 'all') {
            startDateInput.value = '';
            endDateInput.value = '';
        } else {
            const endDate = new Date();
            const startDate = new Date();
            startDate.setDate(startDate.getDate() - parseInt(period));

            startDateInput.value = startDate.toISOString().split('T')[0];
            endDateInput.value = endDate.toISOString().split('T')[0];
        }

        this.applyFiltersAndSort();
    }

    applyDateRange() {
        this.applyFiltersAndSort();
    }

    showBookingDetails(bookingId) {
        const booking = this.allBookings.find(b => b.id === bookingId);
        if (!booking) return;

        const modal = document.getElementById('all-booking-modal');
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
                <p><strong>Status:</strong> <span class="status-badge ${booking.status}">${booking.status.toUpperCase()}</span></p>
            </div>
        `;

        modal.style.display = 'block';
    }

    editBooking(bookingId) {
        // In a real application, this would open an edit form
        alert(`Edit functionality would open here for booking ID: ${bookingId}`);
    }

    exportData() {
        const csvContent = this.filteredBookings.map(booking => {
            return [
                booking.bookingDate.toISOString().split('T')[0],
                booking.name,
                booking.mobile,
                booking.checkIn.toISOString().split('T')[0],
                booking.checkOut.toISOString().split('T')[0],
                this.calculateStayDuration(booking.checkIn, booking.checkOut),
                booking.roomType,
                booking.bookingSource,
                booking.totalAmount,
                booking.status
            ].join(',');
        }).join('\n');

        const header = 'BookingDate,Name,Mobile,CheckIn,CheckOut,Duration,RoomType,BookingSource,TotalAmount,Status\n';
        const blob = new Blob([header + csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `all_bookings_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        window.URL.revokeObjectURL(url);
    }

    startRealTimeUpdates() {
        // Update time every second
        setInterval(() => {
            this.updateDateTime();
        }, 1000);
    }
}

// Initialize the dashboard when the page loads
let allBookings;
document.addEventListener('DOMContentLoaded', () => {
    allBookings = new AllBookingsManager();
});
