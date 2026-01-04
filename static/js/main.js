// Hills Clinic - Main JavaScript

// Counter animation for statistics
function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const animationObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-fade-in');
            
            // Animate counters
            if (entry.target.dataset.counter) {
                const target = parseInt(entry.target.dataset.counter, 10);
                animateCounter(entry.target, target);
            }
            
            animationObserver.unobserve(entry.target);
        }
    });
}, observerOptions);

// Initialize animations on DOM load
document.addEventListener('DOMContentLoaded', () => {
    // Observe elements with animation classes
    document.querySelectorAll('[data-animate]').forEach(el => {
        animationObserver.observe(el);
    });
    
    // Observe counter elements
    document.querySelectorAll('[data-counter]').forEach(el => {
        animationObserver.observe(el);
    });
});

// Timezone detection for booking
function getUserTimezone() {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

// Set timezone in forms
document.querySelectorAll('input[name="timezone"]').forEach(input => {
    if (!input.value) {
        input.value = getUserTimezone();
    }
});

// Mobile menu accessibility
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        // Close any open Alpine.js components
        document.querySelectorAll('[x-data]').forEach(el => {
            if (el.__x) {
                el.__x.$data.mobileMenuOpen = false;
                el.__x.$data.open = false;
            }
        });
    }
});

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^\+?[\d\s-]{10,}$/;
    return re.test(phone);
}

// HTMX event handlers
document.body.addEventListener('htmx:beforeRequest', (e) => {
    // Show loading state
    const target = e.detail.elt;
    if (target.dataset.loadingText) {
        target.dataset.originalText = target.textContent;
        target.textContent = target.dataset.loadingText;
        target.disabled = true;
    }
});

document.body.addEventListener('htmx:afterRequest', (e) => {
    // Restore button state
    const target = e.detail.elt;
    if (target.dataset.originalText) {
        target.textContent = target.dataset.originalText;
        target.disabled = false;
        delete target.dataset.originalText;
    }
});

document.body.addEventListener('htmx:responseError', (e) => {
    console.error('HTMX request failed:', e.detail);
    // Show error toast
    showToast('Something went wrong. Please try again.', 'error');
});

// Toast notification system
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${
        type === 'error' ? 'bg-red-600 text-white' :
        type === 'success' ? 'bg-green-600 text-white' :
        'bg-gray-800 text-white'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Export for use in templates
window.HillsClinic = {
    animateCounter,
    getUserTimezone,
    validateEmail,
    validatePhone,
    showToast
};
