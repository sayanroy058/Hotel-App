// Enhanced Main JavaScript for Hotel Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all features
    initTooltips();
    autoHideAlerts();
    initFormValidation();
    initSearch();
    updateCurrentDate();
    initAnimations();
    initLoadingStates();
    initSmoothScroll();
    
    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
});

// Initialize Bootstrap tooltips
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Auto-hide alerts after 5 seconds with fade effect
function autoHideAlerts() {
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function() {
                bsAlert.close();
            }, 500);
        });
    }, 5000);
}

// Form validation
function initFormValidation() {
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
}

// Enhanced search functionality
function initSearch() {
    const searchInputs = document.querySelectorAll('[data-search-target]');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const target = document.querySelector(input.dataset.searchTarget);
            const searchTerm = input.value.toLowerCase();
            const rows = target.querySelectorAll('tbody tr');
            
            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                    row.style.animation = 'fadeIn 0.3s ease';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
}

// Update current date display
function updateCurrentDate() {
    const now = new Date();
    const dateString = now.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit' 
    });
    
    const dateElements = document.querySelectorAll('.current-date');
    dateElements.forEach(function(el) {
        el.textContent = dateString;
    });
    
    // Also update time if needed
    const timeElements = document.querySelectorAll('.current-time');
    if (timeElements.length > 0) {
        setInterval(function() {
            const now = new Date();
            const timeString = now.toLocaleTimeString();
            timeElements.forEach(function(el) {
                el.textContent = timeString;
            });
        }, 1000);
    }
}

// Initialize scroll animations
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements with animation classes
    document.querySelectorAll('.fade-in, .slide-in-right, .scale-in').forEach(function(el) {
        observer.observe(el);
    });
}

// Handle loading states for buttons
function initLoadingStates() {
    const forms = document.querySelectorAll('form[data-loading]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
                
                // Re-enable after timeout (fallback)
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 10000);
            }
        });
    });
}

// Smooth scrolling for anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
}

// Filter functionality
document.addEventListener('DOMContentLoaded', function() {
    const filterSelects = document.querySelectorAll('[data-filter-target]');
    filterSelects.forEach(function(select) {
        select.addEventListener('change', function() {
            const target = document.querySelector(select.dataset.filterTarget);
            const filterValue = select.value.toLowerCase();
            const rows = target.querySelectorAll('tbody tr');
            
            rows.forEach(function(row) {
                if (!filterValue) {
                    row.style.display = '';
                } else {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(filterValue) ? '' : 'none';
                }
            });
        });
    });
});

// Confirm delete functionality
window.confirmDelete = function(id, name, type) {
    type = type || 'item';
    return confirm('Are you sure you want to delete ' + type + ' "' + name + '"? This action cannot be undone.');
};

// Utility functions
window.HotelUtils = {
    // Format currency
    formatCurrency: function(amount, currency) {
        currency = currency || '₹';
        return currency + parseFloat(amount).toFixed(2);
    },
    
    // Format date
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-IN');
    },
    
    // Calculate days between dates
    daysBetween: function(date1, date2) {
        const oneDay = 24 * 60 * 60 * 1000;
        const firstDate = new Date(date1);
        const secondDate = new Date(date2);
        return Math.round(Math.abs((firstDate - secondDate) / oneDay));
    },
    
    // Show notification
    showNotification: function(message, type) {
        type = type || 'info';
        const alertDiv = document.createElement('div');
        const iconClass = type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle';
        alertDiv.className = 'alert alert-' + type + ' alert-dismissible fade show position-fixed';
        alertDiv.style.cssText = 'top: 80px; right: 20px; z-index: 9999; min-width: 300px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);';
        alertDiv.innerHTML = '<strong><i class="fas fa-' + iconClass + '"></i></strong> ' + 
                             message + 
                             '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(function() {
            if (alertDiv.parentNode) {
                alertDiv.style.opacity = '0';
                alertDiv.style.transform = 'translateX(100%)';
                alertDiv.style.transition = 'all 0.3s ease';
                setTimeout(function() {
                    if (alertDiv.parentNode) {
                        alertDiv.remove();
                    }
                }, 300);
            }
        }, 5000);
    }
};
