const CACHE_NAME = 'devlog-v1';
const URLS_TO_CACHE = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/js/auth.js',
    '/static/js/logEntry.js'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(URLS_TO_CACHE))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});