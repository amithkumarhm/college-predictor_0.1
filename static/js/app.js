// static/js/app.js - Updated with correct place names
// Global app configuration
const CONFIG = {
    API_BASE: '',
    // Updated place names to match database
    PLACES: ['All', 'Bengaluru', 'Mandya', 'Mysore', 'Belagavi', 'Dharwad', 'Hubballi', 'Davanagere', 'Mangaluru', 'Hassan'],
    CATEGORIES: ['GM', 'OBC', 'SC', 'ST'],
    COLLEGE_TYPES: ['MCA', 'MBA', 'MTech'],
    EXAM_TYPES: ['PGCET']
};

// Utility functions
class Utils {
    static showLoading(element) {
        element.innerHTML = `
            <div class="loading">
                <div class="loading-content">
                    <div class="loading-spinner"></div>
                    <p>Analyzing colleges...</p>
                    <div class="typing-indicator">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
            </div>
        `;
    }

    static hideLoading(element) {
        element.innerHTML = '';
    }

    static showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'exclamation' : 'info'}"></i>
                <span>${message}</span>
            </div>
        `;

        document.body.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    static formatCollegeCard(college, matchType) {
        const badgeClass = `match-badge badge-${matchType}`;
        const badgeText = matchType === 'exact' ? '🎯 Exact Match' :
                        matchType === 'near' ? '📈 Near Match' : '📊 Weak Match';

        return `
            <div class="college-card fade-in-up">
                <div class="college-image">
                    <i class="fas fa-university"></i>
                </div>
                <div class="college-content">
                    <div class="${badgeClass}">${badgeText}</div>
                    <h3 class="college-name">${college.college_name}</h3>
                    <div class="college-details">
                        <p><i class="fas fa-id-card"></i> <strong>College ID:</strong> ${college.college_id}</p>
                        <p><i class="fas fa-map-marker-alt"></i> <strong>Location:</strong> ${college.place}, ${college.state}</p>
                        <p><i class="fas fa-chart-line"></i> <strong>Cutoff Range:</strong> ${college.opening_cutoff_rank} - ${college.closing_cutoff_rank}</p>
                        <p><i class="fas fa-users"></i> <strong>Seats:</strong> ${college.seats}</p>
                        <p><i class="fas fa-calendar"></i> <strong>Year:</strong> ${college.year}</p>
                    </div>
                    <a href="${college.website}" target="_blank" class="college-link">
                        <i class="fas fa-external-link-alt"></i>
                        Visit Website
                    </a>
                </div>
            </div>
        `;
    }

    static createParticles() {
        const particlesContainer = document.querySelector('.particles');
        if (!particlesContainer) return;

        for (let i = 0; i < 50; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';

            const size = Math.random() * 6 + 2;
            const posX = Math.random() * 100;
            const duration = Math.random() * 30 + 20;
            const delay = Math.random() * 5;

            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${posX}%`;
            particle.style.animationDuration = `${duration}s`;
            particle.style.animationDelay = `${delay}s`;
            particle.style.opacity = Math.random() * 0.3 + 0.1;
            particle.style.background = `hsl(${Math.random() * 360}, 70%, 60%)`;

            particlesContainer.appendChild(particle);
        }
    }
}

// Local Storage management
class StorageManager {
    static set(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    }

    static get(key) {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    }

    static remove(key) {
        localStorage.removeItem(key);
    }

    static cachePrediction(input, results) {
        const cache = this.get('prediction_cache') || [];
        cache.unshift({ input, results, timestamp: Date.now() });
        // Keep only last 10 predictions
        if (cache.length > 10) cache.pop();
        this.set('prediction_cache', cache);
    }

    static getCachedPrediction(input) {
        const cache = this.get('prediction_cache') || [];
        return cache.find(item =>
            JSON.stringify(item.input) === JSON.stringify(input)
        );
    }
}

// Initialize particles and other effects
document.addEventListener('DOMContentLoaded', function() {
    Utils.createParticles();
});