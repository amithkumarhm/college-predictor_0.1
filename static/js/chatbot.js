// static/js/chatbot.js - Updated with correct place names
class CollegeChatbot {
    constructor() {
        this.conversationState = {
            step: 'welcome',
            data: {}
        };
        this.init();
    }

    init() {
        this.bindEvents();
        this.showWelcomeMessage();
    }

    bindEvents() {
        const chatbotBtn = document.getElementById('chatbotButton');
        const chatbotWindow = document.getElementById('chatbotWindow');
        const sendBtn = document.getElementById('sendMessage');
        const messageInput = document.getElementById('messageInput');

        chatbotBtn.addEventListener('click', () => this.toggleChatbot());
        sendBtn.addEventListener('click', () => this.handleUserInput());

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleUserInput();
        });
    }

    toggleChatbot() {
        const chatbotWindow = document.getElementById('chatbotWindow');
        const isVisible = chatbotWindow.style.display === 'flex';
        chatbotWindow.style.display = isVisible ? 'none' : 'flex';

        if (!isVisible) {
            this.scrollToBottom();
        }
    }

    showWelcomeMessage() {
        this.addMessage('bot', '🤖 Welcome to College Predictor! I can help you find suitable colleges based on your PGCET rank and preferences.');
        this.showNextOptions();
    }

    showNextOptions() {
        const options = this.getOptionsForStep();
        this.showOptions(options);
    }

    getOptionsForStep() {
        switch (this.conversationState.step) {
            case 'welcome':
                return ['🎓 Start Prediction'];
            case 'college_type':
                return CONFIG.COLLEGE_TYPES.map(type => `📚 ${type}`);
            case 'exam_type':
                return CONFIG.EXAM_TYPES.map(exam => `📝 ${exam}`);
            case 'category':
                return CONFIG.CATEGORIES.map(cat => `👤 ${cat}`);
            case 'place':
                return ['🌍 All Locations', ...CONFIG.PLACES.filter(p => p !== 'All').map(place => `📍 ${place}`)];
            case 'rank':
                return ['🔢 Enter Rank'];
            case 'complete':
                return ['🔄 New Prediction', '❌ Close'];
            default:
                return [];
        }
    }

    showOptions(options) {
        const optionsContainer = document.getElementById('chatbotOptions');
        optionsContainer.innerHTML = options.map(option =>
            `<button class="option-btn" onclick="chatbot.handleOptionSelect('${option}')">${option}</button>`
        ).join('');
    }

    handleOptionSelect(option) {
        const cleanOption = option.replace(/[🎓📚📝👤🌍📍🔢🔄❌]/g, '').trim();

        switch (this.conversationState.step) {
            case 'welcome':
                this.conversationState.step = 'college_type';
                this.addMessage('user', 'Start Prediction');
                this.showTypingIndicator();
                setTimeout(() => {
                    this.removeTypingIndicator();
                    this.addMessage('bot', 'Great! Let\'s find your perfect college. Which program are you interested in?');
                    this.showNextOptions();
                }, 1000);
                break;
            case 'college_type':
                this.conversationState.data.college_type = cleanOption;
                this.conversationState.step = 'exam_type';
                this.addMessage('user', cleanOption);
                this.showTypingIndicator();
                setTimeout(() => {
                    this.removeTypingIndicator();
                    this.addMessage('bot', `Excellent choice! ${cleanOption} is a great program. Which exam type?`);
                    this.showNextOptions();
                }, 800);
                break;
            case 'exam_type':
                this.conversationState.data.exam_type = cleanOption;
                this.conversationState.step = 'category';
                this.addMessage('user', cleanOption);
                this.showTypingIndicator();
                setTimeout(() => {
                    this.removeTypingIndicator();
                    this.addMessage('bot', 'What is your category?');
                    this.showNextOptions();
                }, 800);
                break;
            case 'category':
                this.conversationState.data.category = cleanOption;
                this.conversationState.step = 'place';
                this.addMessage('user', cleanOption);
                this.showTypingIndicator();
                setTimeout(() => {
                    this.removeTypingIndicator();
                    this.addMessage('bot', 'Preferred location? Choose "All Locations" to see colleges across Karnataka.');
                    this.showNextOptions();
                }, 800);
                break;
            case 'place':
                this.conversationState.data.place = cleanOption === 'All Locations' ? 'All' : cleanOption;
                this.conversationState.data.state = 'Karnataka';
                this.conversationState.step = 'rank';
                this.addMessage('user', cleanOption);
                this.showTypingIndicator();
                setTimeout(() => {
                    this.removeTypingIndicator();
                    this.addMessage('bot', 'Almost there! Please enter your PGCET rank:');
                    this.showOptions(['🔢 Enter Rank']);
                }, 800);
                return;
            case 'rank':
                if (option.includes('Enter Rank')) {
                    this.showInputField();
                    return;
                }
                break;
            case 'complete':
                if (option.includes('New Prediction')) {
                    this.resetConversation();
                } else {
                    this.toggleChatbot();
                }
                return;
        }
    }

    showInputField() {
        const optionsContainer = document.getElementById('chatbotOptions');
        optionsContainer.innerHTML = `
            <div class="input-group">
                <input type="number" id="rankInput" placeholder="Enter your PGCET rank" min="1">
                <button onclick="chatbot.submitRank()">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        `;
    }

    submitRank() {
        const rankInput = document.getElementById('rankInput');
        const rank = parseInt(rankInput.value);

        if (rank && rank > 0) {
            this.conversationState.data.rank = rank;
            this.addMessage('user', rank.toString());
            this.makePrediction();
        } else {
            this.addMessage('bot', '❌ Please enter a valid rank number (e.g., 1500).');
        }
    }

    async makePrediction() {
        this.showTypingIndicator();

        try {
            const response = await fetch('/chatbot_predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.conversationState.data)
            });

            const results = await response.json();
            this.removeTypingIndicator();
            this.displayPredictionResults(results);
        } catch (error) {
            this.removeTypingIndicator();
            this.addMessage('bot', '❌ Sorry, I encountered an error while processing your request. Please try again.');
        }
    }

    displayPredictionResults(results) {
        let message = '## 🎓 College Prediction Results\\n\\n';

        if (results.exact_matches && results.exact_matches.length > 0) {
            message += '### 🎯 Exact Matches (High Chance)\\n';
            results.exact_matches.slice(0, 5).forEach((college, index) => {
                message += `${index + 1}. **${college.college_name}** - ${college.place}\\n`;
                message += `   📊 Cutoff: ${college.opening_cutoff_rank} - ${college.closing_cutoff_rank}\\n`;
                message += `   👥 Seats: ${college.seats}\\n\\n`;
            });
        }

        if (results.near_matches && results.near_matches.length > 0) {
            message += '### 📈 Near Matches (Good Chance)\\n';
            results.near_matches.slice(0, 3).forEach((college, index) => {
                message += `${index + 1}. **${college.college_name}** - ${college.place}\\n`;
                message += `   📊 Cutoff: ${college.opening_cutoff_rank} - ${college.closing_cutoff_rank}\\n\\n`;
            });
        }

        if (results.weak_matches && results.weak_matches.length > 0) {
            message += '### 📊 Weak Matches (Possible)\\n';
            results.weak_matches.slice(0, 2).forEach((college, index) => {
                message += `${index + 1}. **${college.college_name}** - ${college.place}\\n\\n`;
            });
        }

        if (!results.exact_matches?.length && !results.near_matches?.length && !results.weak_matches?.length) {
            message = '❌ No colleges found matching your criteria. Try adjusting your rank or preferences.';
        } else {
            message += '💡 *Based on historical cutoff data. Actual admission may vary.*';
        }

        this.addMessage('bot', message);
        this.conversationState.step = 'complete';
        this.showNextOptions();
    }

    addMessage(sender, text) {
        const messagesContainer = document.getElementById('chatbotMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${sender}`;

        // Format message with line breaks
        const formattedText = text.replace(/\\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        messageDiv.innerHTML = formattedText;

        messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatbotMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message message-bot typing-animation';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div>Analyzing colleges...</div>
            <div class="typing-dots">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatbotMessages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    resetConversation() {
        this.conversationState = { step: 'welcome', data: {} };
        document.getElementById('chatbotMessages').innerHTML = '';
        this.showWelcomeMessage();
    }

    handleUserInput() {
        const input = document.getElementById('messageInput');
        const text = input.value.trim();

        if (text) {
            this.addMessage('user', text);
            input.value = '';

            // Simple AI response
            this.showTypingIndicator();
            setTimeout(() => {
                this.removeTypingIndicator();
                this.addMessage('bot', 'I understand you typed something, but for the best experience, please use the option buttons to navigate through the prediction process. 😊');
            }, 1500);
        }
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.chatbot = new CollegeChatbot();
});