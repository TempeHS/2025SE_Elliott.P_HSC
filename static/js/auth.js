async signup(form) {
    const formData = {
        email: form.querySelector('input[name="email"]').value,
        password: form.querySelector('input[name="password"]').value
    };

    try {
        const response = await fetch('/api/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify(formData),
            credentials: 'include'
        });

        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            const error = await response.json();
            console.log('Signup error:', error);
        }
    } catch (error) {
        console.log('Network error:', error);
    }
}
