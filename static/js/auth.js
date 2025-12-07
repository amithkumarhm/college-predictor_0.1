// Enhanced Auth JavaScript
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    // Initialize form animations
    initFormAnimations();

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
        initLoginForm();
    }

    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
        initRegisterForm();
    }
});

function initFormAnimations() {
    // Animate form elements on load
    const formElements = document.querySelectorAll('.form-group, .form-options, .auth-submit');
    formElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.6s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function initLoginForm() {
    const inputs = document.querySelectorAll('#loginForm .form-control');
    inputs.forEach(input => {
        // Add focus effects
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
        
        // Add input validation
        input.addEventListener('input', function() {
            validateField(this);
        });
    });
}

function initRegisterForm() {
    const inputs = document.querySelectorAll('#registerForm .form-control');
    inputs.forEach(input => {
        // Add focus effects
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
        
        // Add input validation
        input.addEventListener('input', function() {
            validateField(this);
        });
    });
    
    // Real-time password confirmation validation
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');
    
    if (password && confirmPassword) {
        confirmPassword.addEventListener('input', function() {
            validatePasswordMatch(password, confirmPassword);
        });
    }
}

function validateField(field) {
    const wrapper = field.parentElement;
    
    if (field.value.trim() === '') {
        wrapper.classList.remove('valid', 'invalid');
        return;
    }
    
    let isValid = true;
    
    switch (field.type) {
        case 'email':
            isValid = validateEmail(field.value);
            break;
        case 'text':
            if (field.id === 'username') {
                isValid = field.value.length >= 3 && field.value.length <= 20;
            }
            break;
        case 'password':
            isValid = field.value.length >= 8;
            break;
    }
    
    if (isValid) {
        wrapper.classList.add('valid');
        wrapper.classList.remove('invalid');
    } else {
        wrapper.classList.add('invalid');
        wrapper.classList.remove('valid');
    }
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePasswordMatch(password, confirmPassword) {
    const wrapper = confirmPassword.parentElement;
    
    if (confirmPassword.value === '') {
        wrapper.classList.remove('valid', 'invalid');
        return;
    }
    
    if (password.value === confirmPassword.value && password.value.length >= 8) {
        wrapper.classList.add('valid');
        wrapper.classList.remove('invalid');
    } else {
        wrapper.classList.add('invalid');
        wrapper.classList.remove('valid');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        username: formData.get('username'),
        password: formData.get('password')
    };

    // Show loading state
    const submitBtn = e.target.querySelector('.auth-submit');
    submitBtn.classList.add('loading');

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(data)
        });

        if (response.ok) {
            // Success animation
            submitBtn.classList.add('success');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            submitBtn.classList.remove('loading');
            showError('Invalid credentials. Please try again.');
        }
    } catch (error) {
        submitBtn.classList.remove('loading');
        showError('An error occurred. Please try again.');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const data = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password')
    };

    // Validate passwords match
    const password = formData.get('password');
    const confirmPassword = formData.get('confirmPassword');
    
    if (password !== confirmPassword) {
        showError('Passwords do not match.');
        return;
    }
    
    if (password.length < 8) {
        showError('Password must be at least 8 characters long.');
        return;
    }

    // Show loading state
    const submitBtn = e.target.querySelector('.auth-submit');
    submitBtn.classList.add('loading');

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams(data)
        });

        if (response.ok) {
            // Success animation
            submitBtn.classList.add('success');
            setTimeout(() => {
                window.location.href = '/login';
            }, 1000);
        } else {
            submitBtn.classList.remove('loading');
            showError('Registration failed. Please try again.');
        }
    } catch (error) {
        submitBtn.classList.remove('loading');
        showError('An error occurred. Please try again.');
    }
}

function showError(message) {
    // Remove existing error messages
    const existingErrors = document.querySelectorAll('.error-message');
    existingErrors.forEach(error => error.remove());
    
    // Create new error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        ${message}
    `;
    
    const form = document.querySelector('form');
    form.insertBefore(errorDiv, form.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Add CSS for validation states
const style = document.createElement('style');
style.textContent = `
    .input-wrapper.valid .form-control {
        border-color: #10b981;
    }
    
    .input-wrapper.invalid .form-control {
        border-color: #ef4444;
    }
    
    .input-wrapper.focused .form-control {
        border-color: var(--primary-color);
    }
    
    .auth-submit.success {
        background: linear-gradient(135deg, #10b981, #059669) !important;
    }
`;
document.head.appendChild(style);