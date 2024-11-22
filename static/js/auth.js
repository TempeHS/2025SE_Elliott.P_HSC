export class Auth {
    constructor() {
        this.setupUI();
        this.bindEvents();
        this.csrfToken = document.querySelector('meta[name="csrf-token"]').content;
    }

    setupUI() {
        const authSection = document.getElementById('authSection');
        if (!authSection) return;
    }

    bindEvents() {
        const loginForm = document.getElementById('loginForm');
        const signupForm = document.getElementById('signupForm');
        const searchForm = document.getElementById('searchForm');

        if (loginForm) {
            loginForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                await this.login(new FormData(loginForm));
            });
        }

        if (signupForm) {
            signupForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                await this.signup(new FormData(signupForm));
            });
        }

        if (searchForm) {
            searchForm.addEventListener('submit', async (event) => {
                event.preventDefault();
                await this.searchEntries(new FormData(searchForm));
            });
        }
    }

    async login(form) {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.csrfToken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(Object.fromEntries(form))
        });
        const data = await response.json();
        if (response.ok) {
            window.location.href = '/';
        } else {
            console.error(data.error);
        }
    }

    async signup(form) {
        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.csrfToken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(Object.fromEntries(form))
        });
        const data = await response.json();
        if (response.ok) {
            window.location.href = '/';
        } else {
            console.error(data.error);
        }
    }

    async searchEntries(form) {
        const params = new URLSearchParams(Object.fromEntries(form));
        const response = await fetch(`/api/entries/search?${params.toString()}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        if (response.ok) {
            this.displayResults(data);
        } else {
            console.error(data.error);
        }
    }

    displayResults(entries) {
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = '';
        entries.forEach(entry => {
            const entryDiv = document.createElement('div');
            entryDiv.className = 'entry';
            entryDiv.innerHTML = `
                <h3>${entry.project}</h3>
                <p>${entry.date}</p>
                <p>${entry.developer_tag}</p>
            `;
            resultsDiv.appendChild(entryDiv);
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new Auth();
});