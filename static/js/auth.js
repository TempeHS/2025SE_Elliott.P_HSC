document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const logoutBtn = document.getElementById('logoutBtn');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Login form submitted');
            
            const formData = {
                email: document.getElementById('email').value,
                password: document.getElementById('password').value
            };
            console.log('Form data prepared:', formData);

            try {
                console.log('Sending login request...');
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify(formData)
                });
                console.log('Response received:', response);

                const data = await response.json();
                console.log('Response data:', data);
                
                if (response.ok) {
                    window.location.href = data.redirect;
                } else {
                    throw new Error(data.error);
                }
            } catch (error) {
                console.error('Login error:', error);
                const errorDiv = document.getElementById('loginError');
                if (errorDiv) {
                    errorDiv.textContent = error.message;
                    errorDiv.style.display = 'block';
                }
            }
        });
    }

    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Signup form submitted');
            
            const formData = {
                email: document.getElementById('email').value,
                password: document.getElementById('password').value,
                developer_tag: document.getElementById('developer_tag').value
            };
            console.log('Form data prepared:', formData);

            try {
                console.log('Sending signup request...');
                const response = await fetch('/api/auth/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify(formData)
                });
                console.log('Response received:', response);

                const data = await response.json();
                console.log('Response data:', data);
                
                if (response.ok) {
                    window.location.href = data.redirect;
                } else {
                    throw new Error(data.error);
                }
            } catch (error) {
                console.error('Signup error:', error);
                const errorDiv = document.getElementById('signupError');
                if (errorDiv) {
                    errorDiv.textContent = error.message;
                    errorDiv.style.display = 'block';
                }
            }
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                const response = await fetch('/api/auth/logout', {
                    method: 'POST',
                    headers: {
                        'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
                    }
                });
                const data = await response.json();
                if (response.ok) {
                    window.location.href = data.redirect;
                }
            } catch (error) {
                console.error('Logout failed:', error);
            }
        });
    }
});
