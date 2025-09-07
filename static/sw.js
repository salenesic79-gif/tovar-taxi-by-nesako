const CACHE_NAME = 'tovar-taxi-v1.0.0';
const STATIC_CACHE = 'tovar-taxi-static-v1';
const DYNAMIC_CACHE = 'tovar-taxi-dynamic-v1';

// Files to cache immediately
const STATIC_FILES = [
    '/',
    '/static/css/animations.css',
    '/static/css/responsive.css',
    '/static/css/popup-styles.css',
    '/static/js/modern-effects.js',
    '/static/js/notifications.js',
    '/static/images/TTaxi9_icon.ico.png',
    '/static/images/TTaxi9_icon.ico.png',
    '/static/manifest.json',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
    'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap'
];

// API endpoints that should work offline
const API_ENDPOINTS = [
    '/transport/shipper-dashboard/',
    '/transport/carrier-dashboard/',
    '/transport/notifications/',
    '/transport/my-tours/',
    '/transport/manage-vehicles/'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
    console.log('[SW] Installing service worker...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('[SW] Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .catch((error) => {
                console.error('[SW] Failed to cache static files:', error);
            })
    );
    self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating service worker...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                        console.log('[SW] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Handle different types of requests
    if (STATIC_FILES.some(file => request.url.includes(file))) {
        // Cache first strategy for static files
        event.respondWith(cacheFirst(request));
    } else if (API_ENDPOINTS.some(endpoint => request.url.includes(endpoint))) {
        // Network first strategy for API endpoints
        event.respondWith(networkFirst(request));
    } else if (request.url.includes('/static/')) {
        // Cache first for other static assets
        event.respondWith(cacheFirst(request));
    } else if (request.destination === 'document') {
        // Network first for HTML pages
        event.respondWith(networkFirst(request));
    } else {
        // Default: try network, fallback to cache
        event.respondWith(networkFirst(request));
    }
});

// Cache first strategy
async function cacheFirst(request) {
    try {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(STATIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.error('[SW] Cache first failed:', error);
        return new Response('Offline - content not available', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

// Network first strategy
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.log('[SW] Network failed, trying cache:', request.url);
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Return offline page for navigation requests
        if (request.destination === 'document') {
            return caches.match('/') || new Response(getOfflineHTML(), {
                headers: { 'Content-Type': 'text/html' }
            });
        }
        
        return new Response('Offline', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

// Background sync for form submissions
self.addEventListener('sync', (event) => {
    console.log('[SW] Background sync triggered:', event.tag);
    
    if (event.tag === 'shipment-sync') {
        event.waitUntil(syncShipments());
    } else if (event.tag === 'notification-sync') {
        event.waitUntil(syncNotifications());
    }
});

// Sync pending shipments
async function syncShipments() {
    try {
        const cache = await caches.open(DYNAMIC_CACHE);
        const pendingRequests = await cache.keys();
        
        for (const request of pendingRequests) {
            if (request.url.includes('/transport/create-shipment/')) {
                try {
                    await fetch(request);
                    await cache.delete(request);
                    console.log('[SW] Synced shipment:', request.url);
                } catch (error) {
                    console.error('[SW] Failed to sync shipment:', error);
                }
            }
        }
    } catch (error) {
        console.error('[SW] Background sync failed:', error);
    }
}

// Sync notifications
async function syncNotifications() {
    try {
        const response = await fetch('/transport/api/notifications/');
        if (response.ok) {
            const notifications = await response.json();
            // Send notifications to all clients
            const clients = await self.clients.matchAll();
            clients.forEach(client => {
                client.postMessage({
                    type: 'NOTIFICATIONS_UPDATE',
                    notifications: notifications
                });
            });
        }
    } catch (error) {
        console.error('[SW] Failed to sync notifications:', error);
    }
}

// Push notification handler
self.addEventListener('push', (event) => {
    console.log('[SW] Push notification received');
    
    const options = {
        body: 'Nova notifikacija u Tovar Taxi aplikaciji',
        icon: '/static/images/TTaxi9_icon.ico.png',
        badge: '/static/images/TTaxi9_icon.ico.png',
        vibrate: [200, 100, 200],
        data: {
            url: '/transport/notifications/'
        },
        actions: [
            {
                action: 'open',
                title: 'Otvori',
                icon: '/static/images/TTaxi9_icon.ico.png'
            },
            {
                action: 'close',
                title: 'Zatvori'
            }
        ]
    };

    if (event.data) {
        const data = event.data.json();
        options.body = data.message || options.body;
        options.data.url = data.url || options.data.url;
    }

    event.waitUntil(
        self.registration.showNotification('Tovar Taxi', options)
    );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
    console.log('[SW] Notification clicked');
    event.notification.close();

    if (event.action === 'open' || !event.action) {
        event.waitUntil(
            clients.openWindow(event.notification.data.url || '/')
        );
    }
});

// Offline HTML fallback
function getOfflineHTML() {
    return `
    <!DOCTYPE html>
    <html lang="sr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Offline - Tovar Taxi</title>
        <style>
            body {
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
                color: white;
                text-align: center;
            }
            .offline-container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }
            .offline-icon {
                font-size: 64px;
                margin-bottom: 20px;
            }
            .offline-title {
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 10px;
            }
            .offline-message {
                font-size: 16px;
                opacity: 0.8;
                margin-bottom: 20px;
            }
            .retry-button {
                background: #FFD700;
                color: #000;
                border: none;
                padding: 12px 24px;
                border-radius: 25px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .retry-button:hover {
                background: #FFC107;
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="offline-container">
            <div class="offline-icon">📱</div>
            <div class="offline-title">Nema internetske veze</div>
            <div class="offline-message">
                Proverite internetsku vezu i pokušajte ponovo.
            </div>
            <button class="retry-button" onclick="window.location.reload()">
                Pokušaj ponovo
            </button>
        </div>
    </body>
    </html>
    `;
}

// Message handler for communication with main thread
self.addEventListener('message', (event) => {
    console.log('[SW] Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

console.log('[SW] Service worker loaded successfully');
