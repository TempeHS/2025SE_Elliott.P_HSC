if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
        navigator.serviceWorker.register("/service-worker.js").then(function (registration) {
            console.log("ServiceWorker registration successful with scope: ", registration.scope);
        }, function (err) {
            console.log("ServiceWorker registration failed: ", err);
        });
    });
}

document.addEventListener("DOMContentLoaded", function () {
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
});