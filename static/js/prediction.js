// static/js/prediction.js - Updated with correct place names
class PredictionManager {
    constructor() {
        this.currentInput = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadCachedData();
    }

    bindEvents() {
        const predictionForm = document.getElementById('predictionForm');
        if (predictionForm) {
            predictionForm.addEventListener('submit', (e) => this.handlePrediction(e));
        }

        // Populate dropdowns with correct place names
        this.populateDropdown('place', CONFIG.PLACES);
        this.populateDropdown('category', CONFIG.CATEGORIES);
        this.populateDropdown('college_type', CONFIG.COLLEGE_TYPES);
        this.populateDropdown('exam_type', CONFIG.EXAM_TYPES);
    }

    populateDropdown(elementId, options) {
        const select = document.getElementById(elementId);
        if (select) {
            // Clear existing options except the first one
            while (select.options.length > 1) {
                select.remove(1);
            }

            // Add new options
            options.forEach(option => {
                const optionElement = document.createElement('option');
                optionElement.value = option;
                optionElement.textContent = option;
                select.appendChild(optionElement);
            });
        }
    }

    async handlePrediction(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        this.currentInput = {
            exam_type: formData.get('exam_type'),
            state: 'Karnataka',
            place: formData.get('place'),
            rank: parseInt(formData.get('rank')),
            category: formData.get('category'),
            college_type: formData.get('college_type')
        };

        console.log('Prediction input:', this.currentInput);

        // Check cache first
        const cached = StorageManager.getCachedPrediction(this.currentInput);
        if (cached) {
            this.displayResults(cached.results);
            // Scroll to results
            this.scrollToResults();
            return;
        }

        await this.makePrediction(this.currentInput);
    }

    async makePrediction(input) {
        const resultsContainer = document.getElementById('predictionResults');
        Utils.showLoading(resultsContainer);

        try {
            console.log('Making prediction request with data:', input);

            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(input)
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }

            const results = await response.json();
            console.log('Prediction results:', results);

            // Cache the results
            StorageManager.cachePrediction(input, results);

            this.displayResults(results);

            // Auto-scroll to results
            setTimeout(() => this.scrollToResults(), 100);

        } catch (error) {
            console.error('Prediction error:', error);
            resultsContainer.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Prediction failed!</strong><br>
                    ${error.message}<br>
                    <small>Please check your inputs and try again.</small>
                </div>
            `;
        }
    }

    scrollToResults() {
        const resultsSection = document.getElementById('predictionResults');
        if (resultsSection) {
            resultsSection.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    }

    displayResults(results) {
        const container = document.getElementById('predictionResults');
        let html = '';

        // Check if we have exact matches
        const hasExactMatches = results.exact_matches && results.exact_matches.length > 0;

        if (!hasExactMatches) {
            html = `
                <div class="no-results fade-in-up">
                    <div class="no-results-icon">
                        <i class="fas fa-search"></i>
                    </div>
                    <h3>No Exact Matches Found</h3>
                    <p>No colleges match your current criteria with exact cutoff range.</p>
                    <div class="suggestions">
                        <p><strong>Debug Information:</strong></p>
                        <ul>
                            <li><strong>Rank:</strong> ${this.currentInput?.rank || 'N/A'}</li>
                            <li><strong>Category:</strong> ${this.currentInput?.category || 'N/A'}</li>
                            <li><strong>Location:</strong> ${this.currentInput?.place || 'N/A'}</li>
                            <li><strong>Program:</strong> ${this.currentInput?.college_type || 'N/A'}</li>
                        </ul>
                        <p><strong>Suggestions:</strong></p>
                        <ul>
                            <li>Try adjusting your rank slightly</li>
                            <li>Check if the category is correct</li>
                            <li>Try "All" for location to see all colleges</li>
                            <li>Verify the program type matches</li>
                        </ul>
                    </div>
                </div>
            `;
        } else {
            html = `
                <div class="results-header fade-in-up">
                    <h2>🎯 Exact Matches Found</h2>
                    <p class="results-count">${results.exact_matches.length} colleges match your criteria</p>
                </div>
                <div class="college-results-grid">
                    ${results.exact_matches.map(college => this.formatCollegeCard(college)).join('')}
                </div>
            `;
        }

        container.innerHTML = html;

        // Update step indicator
        if (typeof updateStepIndicatorToResults === 'function') {
            updateStepIndicatorToResults();
        }
    }

    formatCollegeCard(college) {
        // Ensure all required fields are present
        const collegeName = college.college_name || 'Unknown College';
        const collegeId = college.college_id || 'N/A';
        const place = college.place || 'Unknown Location';
        const state = college.state || 'Karnataka';
        const openingRank = college.opening_cutoff_rank || 'N/A';
        const closingRank = college.closing_cutoff_rank || 'N/A';
        const website = college.website || '#';
        const year = college.year || 'N/A';

        return `
            <div class="college-card fade-in-up">
                <div class="college-background">
                    <i class="fas fa-university"></i>
                </div>
                <div class="college-content">
                    <h3 class="college-name">${collegeName}</h3>
                    <div class="college-details">
                        <div class="detail-item">
                            <i class="fas fa-id-card"></i>
                            <strong>ID:</strong> ${collegeId}
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-map-marker-alt"></i>
                            <strong>Location:</strong> ${place}, ${state}
                        </div>
                        <div class="detail-item">
                            <i class="fas fa-chart-line"></i>
                            <strong>Cutoff (${year}):</strong> ${openingRank} - ${closingRank}
                        </div>
                    </div>
                    <div class="college-actions">
                        <a href="${website}" target="_blank" class="college-link" onclick="event.stopPropagation();">
                            <i class="fas fa-external-link-alt"></i>
                            Visit Website
                        </a>
                    </div>
                </div>
            </div>
        `;
    }

    loadCachedData() {
        // Load any cached form data
        const cachedForm = StorageManager.get('prediction_form');
        if (cachedForm) {
            Object.keys(cachedForm).forEach(key => {
                const element = document.getElementById(key);
                if (element) element.value = cachedForm[key];
            });
        }
    }
}

// Initialize prediction manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.predictionManager = new PredictionManager();
});