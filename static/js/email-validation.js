// Email validation with AJAX
class EmailValidator {
    constructor(emailInputId, messageContainerId, validationUrl) {
        console.log('EmailValidator constructor called with:', { emailInputId, messageContainerId, validationUrl });
        this.emailInput = document.getElementById(emailInputId);
        this.messageContainer = document.getElementById(messageContainerId);
        this.validationUrl = validationUrl;
        this.timeout = null;
        this.isValidating = false;

        console.log('EmailValidator elements found:', {
            emailInput: this.emailInput,
            messageContainer: this.messageContainer
        });

        if (this.emailInput && this.messageContainer) {
            this.init();
            console.log('EmailValidator initialized successfully');
        } else {
            console.warn('EmailValidator initialization failed - missing elements');
        }
    }

    init() {
        // Add event listener for input changes
        this.emailInput.addEventListener('input', () => {
            this.debounceValidation();
        });

        // Add event listener for blur (when user leaves the field)
        this.emailInput.addEventListener('blur', () => {
            if (this.emailInput.value.trim()) {
                this.validateEmail();
            }
        });

        // Clear message when user starts typing
        this.emailInput.addEventListener('focus', () => {
            this.clearMessage();
        });
    }

    debounceValidation() {
        // Clear existing timeout
        if (this.timeout) {
            clearTimeout(this.timeout);
        }

        // Set new timeout for 3 seconds
        this.timeout = setTimeout(() => {
            if (this.emailInput.value.trim()) {
                this.validateEmail();
            } else {
                this.clearMessage();
            }
        }, 3000);
    }

    validateEmail() {
        if (this.isValidating) return;

        const email = this.emailInput.value.trim();
        if (!email) {
            this.clearMessage();
            return;
        }

        this.isValidating = true;
        this.showMessage('Validating email...', 'info');

        // Create form data
        const formData = new FormData();
        formData.append('email', email);
        formData.append('csrfmiddlewaretoken', this.getCSRFToken());

        // Make AJAX request
        fetch(this.validationUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
            .then(response => response.json())
            .then(data => {
                this.isValidating = false;
                if (data.valid) {
                    this.showMessage(data.message, 'success');
                    this.emailInput.classList.remove('is-invalid');
                    this.emailInput.classList.add('is-valid');
                } else {
                    this.showMessage(data.message, 'error');
                    this.emailInput.classList.remove('is-valid');
                    this.emailInput.classList.add('is-invalid');
                }
            })
            .catch(error => {
                this.isValidating = false;
                console.error('Email validation error:', error);
                this.showMessage('Validation failed. Please try again.', 'error');
                this.emailInput.classList.remove('is-valid');
                this.emailInput.classList.add('is-invalid');
            });
    }

    showMessage(message, type) {
        this.messageContainer.innerHTML = `
            <div class="email-validation-message ${type}">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        this.messageContainer.style.display = 'block';
    }

    clearMessage() {
        this.messageContainer.innerHTML = '';
        this.messageContainer.style.display = 'none';
        this.emailInput.classList.remove('is-valid', 'is-invalid');
    }

    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
}

// Restaurant name validation with AJAX
class RestaurantNameValidator {
    constructor(nameInputId, messageContainerId, validationUrl) {
        this.nameInput = document.getElementById(nameInputId);
        this.messageContainer = document.getElementById(messageContainerId);
        this.validationUrl = validationUrl;
        this.timeout = null;
        this.isValidating = false;

        if (this.nameInput && this.messageContainer) {
            this.init();
        }
    }

    init() {
        // Add event listener for input changes
        this.nameInput.addEventListener('input', () => {
            this.debounceValidation();
        });

        // Add event listener for blur (when user leaves the field)
        this.nameInput.addEventListener('blur', () => {
            if (this.nameInput.value.trim()) {
                this.validateRestaurantName();
            }
        });

        // Clear message when user starts typing
        this.nameInput.addEventListener('focus', () => {
            this.clearMessage();
        });
    }

    debounceValidation() {
        // Clear existing timeout
        if (this.timeout) {
            clearTimeout(this.timeout);
        }

        // Set new timeout for 2 seconds
        this.timeout = setTimeout(() => {
            if (this.nameInput.value.trim()) {
                this.validateRestaurantName();
            } else {
                this.clearMessage();
            }
        }, 2000);
    }

    validateRestaurantName() {
        if (this.isValidating) return;

        const restaurantName = this.nameInput.value.trim();
        if (!restaurantName) {
            this.clearMessage();
            return;
        }

        this.isValidating = true;
        this.showMessage('Checking restaurant name...', 'info');

        // Create form data
        const formData = new FormData();
        formData.append('restaurant_name', restaurantName);
        formData.append('csrfmiddlewaretoken', this.getCSRFToken());

        // Make AJAX request
        fetch(this.validationUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
            .then(response => response.json())
            .then(data => {
                this.isValidating = false;
                if (data.valid) {
                    this.showMessage(data.message, 'success');
                    this.nameInput.classList.remove('is-invalid');
                    this.nameInput.classList.add('is-valid');
                } else {
                    this.showMessage(data.message, 'error');
                    this.nameInput.classList.remove('is-valid');
                    this.nameInput.classList.add('is-invalid');
                }
            })
            .catch(error => {
                this.isValidating = false;
                console.error('Restaurant name validation error:', error);
                this.showMessage('Validation failed. Please try again.', 'error');
                this.nameInput.classList.remove('is-valid');
                this.nameInput.classList.add('is-invalid');
            });
    }

    showMessage(message, type) {
        this.messageContainer.innerHTML = `
            <div class="restaurant-name-validation-message ${type}">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        this.messageContainer.style.display = 'block';
    }

    clearMessage() {
        this.messageContainer.innerHTML = '';
        this.messageContainer.style.display = 'none';
        this.nameInput.classList.remove('is-valid', 'is-invalid');
    }

    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }
}

// Initialize email validators when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    console.log('Email validation script loaded');

    // Skip email validation for login form - users are logging in with existing emails
    // Only validate for registration forms

    // Initialize for business registration page
    const businessEmailInput = document.getElementById('business-email');
    console.log('Business email input found:', businessEmailInput);
    if (businessEmailInput) {
        new EmailValidator('business-email', 'business-email-message', '/users/validate-email/');
    }

    // Initialize for regular registration page (login form)
    const registerEmailInput = document.getElementById('reg-email');
    console.log('Register email input found:', registerEmailInput);
    if (registerEmailInput) {
        new EmailValidator('reg-email', 'register-email-message', '/users/validate-email/');
    }

    // Initialize restaurant name validation for business registration
    const restaurantNameInput = document.getElementById('restaurant-name');
    console.log('Restaurant name input found:', restaurantNameInput);
    if (restaurantNameInput) {
        new RestaurantNameValidator('restaurant-name', 'restaurant-name-message', '/users/validate-restaurant-name/');
    }
});
