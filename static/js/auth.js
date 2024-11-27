export class Auth {
    constructor() {
        this.setupUI();
        this.bindEvents();
    }

    setupUI() {
        const authSection = document.getElementById('authSection');
        authSection.innerHTML = `
            <div class="card" id="authCard">
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
                                    <input type="email" class="form-control" placeholder="Email" required>
                                </div>
                                <div class="mb-3">
                                    <input type="password" class="form-control" placeholder="Password" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Login</button>
                            </form>
                        </div>
                        <div class="tab-pane fade" id="signup">
                            <form id="signupForm">
                                <div class="mb-3">
                                    <input type="email" class="form-control" placeholder="Email" required>
                                </div>
                                <div class="mb-3">
                                    <input type="password" class="form-control" placeholder="Password" required>
                                </div>
                                <button type="submit" class="btn btn-primary">Sign Up</button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.login(e.target);
        });

        document.getElementById('signupForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.signup(e.target);
        });
    }

    async login(form) {
        const data = {
            email: form.querySelector('input[type="email"]').value,
            password: form.querySelector('input[type="password"]').value
        };

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                window.location.reload();
            } else {
                const result = await response.json();
                console.error('Login failed:', result.error);
            }
        } catch (error) {
            console.error('Login error:', error);
        }
    }

    async signup(form) {
        const data = {
            email: form.querySelector('input[type="email"]').value,
            password: form.querySelector('input[type="password"]').value
        };

        try {
            const response = await fetch('/api/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                window.location.reload();
            } else {
                const result = await response.json();
                console.error('Signup failed:', result.error);
            }
        } catch (error) {
            console.error('Signup error:', error);
        }
    }

    async checkAuthStatus() {
        const userInfo = document.getElementById('userInfo');
        try {
            const response = await fetch('/api/user');
            if (response.ok) {
                const data = await response.json();
                document.getElementById('authSection').style.display = 'none';
                userInfo.innerHTML = `
                    <span>${data.email}</span>
                    <button class="btn btn-outline-light ms-2" onclick="logout()">Logout</button>
                `;
            }
        } catch (error) {
            console.error('Auth check error:', error);
        }
    }
}