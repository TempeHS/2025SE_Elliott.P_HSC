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
    if (link.getAttribute("href") === currentUrl) {
      link.classList.add("active");
    }
  });

  document.getElementById('newEntryNav').addEventListener('click', () => {
    logEntry.setupUI();
  });

  document.getElementById('searchNav').addEventListener('click', () => {
    logEntry.setupSearchUI();
  });
});

// this basically checks if the service worker is supported by the browser