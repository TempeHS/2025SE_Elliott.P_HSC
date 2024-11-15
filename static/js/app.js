import { Auth } from './auth.js';
import { LogEntry } from './logEntry.js';

if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
        navigator.serviceWorker
            .register("static/js/serviceWorker.js")
            .then((res) => console.log("service worker registered"))
            .catch((err) => console.log("service worker not registered", err));
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const navLinks = document.querySelectorAll(".nav-link");
    const currentUrl = window.location.pathname;

    navLinks.forEach((link) => {
        const linkUrl = link.getAttribute("href");
        if (linkUrl === currentUrl) {
            link.classList.add("active");
            link.setAttribute("aria-current", "page");
        } else {
            link.classList.remove("active");
            link.removeAttribute("aria-current");
        }
    });

    const auth = new Auth();
    const logEntry = new LogEntry();
    
    auth.checkAuthStatus();
});