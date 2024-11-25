export class Auth {
    constructor() {
        console.log('Auth class initialized');
        this.setupUI();
        this.bindEvents();
        this.csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    }

    setupUI() {
        this.loginForm = document.getElementById('loginForm');
        this.signupForm = document.getElementById('signupForm');
    }

    bindEvents() {
        if (this.loginForm) {
            this.loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(this.loginForm);
                await this.login(formData);
            });
        }

        if (this.signupForm) {
            this.signupForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(this.signupForm);
                await this.signup(formData);
            });
        }
    }

    async login(formData) {
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(Object.fromEntries(formData)),
                credentials: 'same-origin'
            });

            const data = await response.json();
            if (response.ok) {
                window.location.href = data.redirect || '/';
            } else {
                alert(data.error || 'Login failed');
            }
        } catch (error) {
            alert('Login failed. Please try again.');
        }
    }

    async signup(formData) {
        try {
            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(Object.fromEntries(formData)),
                credentials: 'same-origin'
            });

            const data = await response.json();
            if (response.ok) {
                window.location.href = data.redirect || '/';
            } else {
                alert(data.error || 'Signup failed');
            }
        } catch (error) {
            alert('Signup failed. Please try again.');
        }
    }
}

// Initialize auth when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new Auth();
});