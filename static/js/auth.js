export class Auth {
    constructor() {
        this.setupUI();
        this.bindEvents();
        this.checkAuthStatus();
    }

    setupUI() {
        const authSection = document.getElementById('authSection');
        authSection.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <ul class="nav nav-tabs" role="tablist">
                        <li class="nav-item">
                            <a class="nav-link active" data-bs-toggle="tab" href="#login">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" data-bs-toggle="tab" href="#signup">Sign Up</a>
                        </li>
                    </ul>
                    <div class="tab-content mt-3">
                        <div class="tab-pane fade show active" id="login">
                            <form id="loginForm">
                                <div class="mb-3">
                                    <input type="email" class="form-control" name="email" placeholder="Email" required>
                                </div>
                                <div class="mb-3">
                                    <input type="password" class="form-control" name="password" placeholder="Password" required>
                                </div>
                                <div id="loginError" class="alert alert-danger d-none"></div>
                                <button type="submit" class="btn btn-primary">Login</button>
                            </form>
                        </div>
                        <div class="tab-pane fade" id="signup">
                            <form id="signupForm">
                                <div class="mb-3">
                                    <input type="email" class="form-control" name="email" placeholder="Email" required>
                                </div>
                                <div class="mb-3">
                                    <input type="password" class="form-control" name="password" placeholder="Password" required>
                                </div>
                                <div id="signupError" class="alert alert-danger d-none"></div>
                                <button type="submit" class="btn btn-primary">Sign Up</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        const loginForm = document.getElementById('loginForm');
        const signupForm = document.getElementById('signupForm');

        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.login(e.target);
        });

        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.signup(e.target);
        });
    }

    async login(form) {
        const formData = {
            email: form.querySelector('input[name="email"]').value,
            password: form.querySelector('input[name="password"]').value
        };

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('userEmail', formData.email);
                window.location.href = '/dashboard';
            } else {
                const errorDiv = document.getElementById('loginError');
                errorDiv.textContent = data.error || 'Login failed';
                errorDiv.classList.remove('d-none');
            }
        } catch (error) {
            console.error('Login error:', error);
        }
    }

    async signup(form) {
        const formData = {
            email: form.querySelector('input[name="email"]').value,
            password: form.querySelector('input[name="password"]').value
        };

        try {
            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('userEmail', formData.email);
                window.location.href = '/dashboard';
            } else {
                const errorDiv = document.getElementById('signupError');
                errorDiv.textContent = data.error || 'Signup failed';
                errorDiv.classList.remove('d-none');
            }
        } catch (error) {
            console.error('Signup error:', error);
        }
    }

    async checkAuthStatus() {
        try {
            const response = await fetch('/api/auth/user');
            if (response.ok) {
                const data = await response.json();
                document.getElementById('authSection').style.display = 'none';
                const userInfo = document.getElementById('userInfo');
                userInfo.innerHTML = `
                    <span>${data.email}</span>
                    <button class="btn btn-outline-light ms-2" onclick="logout()">Logout</button>
                `;
            }
        } catch (error) {
            console.error('Auth check error:', error);
        }
    }

    static async logout() {
        try {
            const response = await fetch('/api/auth/logout', {
                method: 'POST'
            });

            if (response.ok) {
                localStorage.removeItem('userEmail');
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Logout error:', error);
        }
    }
}

window.logout = Auth.logout;
