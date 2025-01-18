import { Auth } from './auth.js';
import { LogEntry } from './logEntry.js';

if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker
      .register("/static/js/serviceWorker.js")
      .then((res) => console.log("Service worker registered"))
      .catch((err) => console.log("Service worker not registered", err));
  });
}

document.addEventListener("DOMContentLoaded", async function () {
  const response = await fetch('/api/user');
  if (!response.ok) {
    window.location.href = '/login';
    return;
  }

  const auth = new Auth();
  auth.checkAuthStatus();

  const logEntry = new LogEntry();

  const navLinks = document.querySelectorAll(".nav-link");
  const currentUrl = window.location.pathname;

    navLinks.forEach((link) => {
        const linkUrl = link.getAttribute("href");
        if (linkUrl === currentUrl) {
            link.classList.add("active");
        } else {
            link.classList.remove("active");
        }
    });

    // Initialize Auth class
    new Auth();

    // Handle diary entry form submission
    const entryForm = document.getElementById('entryForm');
    if (entryForm) {
        entryForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(entryForm);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await fetch('/api/entries', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
                    },
                    body: JSON.stringify(data),
                    credentials: 'same-origin'
                });

                const result = await response.json();
                if (response.ok) {
                    alert('Entry created successfully');
                    // Optionally, redirect or update the UI
                } else {
                    alert(result.error || 'Failed to create entry');
                }
            } catch (error) {
                alert('Failed to create entry. Please try again.');
            }
        });
    }
});