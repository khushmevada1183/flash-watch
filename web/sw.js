// Service Worker for boAt FLASH Watch Web App
const CACHE_NAME = 'flash-watch-v4';
const ASSETS = [
  './',
  'index.html',
  'icon.svg',
  'manifest.webmanifest'
];

self.addEventListener('install', (e) => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  // Pass API calls (bridge mode) through to network directly
  if (e.request.url.includes('/api/')) {
    return;
  }

  // Network-first for HTML / navigation to ensure instant updates
  if (e.request.mode === 'navigate' || e.request.destination === 'document') {
    e.respondWith(
      fetch(e.request)
        .then((res) => {
          const resClone = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(e.request, resClone));
          return res;
        })
        .catch(() => caches.match(e.request).then((res) => res || caches.match('./')))
    );
    return;
  }

  // Cache-first with network fallback for static assets
  e.respondWith(
    caches.match(e.request).then((res) => res || fetch(e.request))
  );
});
