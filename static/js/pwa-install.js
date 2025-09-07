// PWA Install and Enhanced Functionality
class PWAManager {
    constructor() {
        this.deferredPrompt = null;
        this.isInstalled = false;
        this.swRegistration = null;
        this.init();
    }

    async init() {
        // Register service worker
        await this.registerServiceWorker();
        
        // Setup install prompt
        this.setupInstallPrompt();
        
        // Setup app update handling
        this.setupAppUpdates();
        
        // Setup push notifications
        this.setupPushNotifications();
        
        // Setup background sync
        this.setupBackgroundSync();
        
        // Check if already installed
        this.checkInstallStatus();
        
        console.log('[PWA] Manager initialized');
    }

    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                this.swRegistration = await navigator.serviceWorker.register('/static/sw.js', {
                    scope: '/'
                });
                
                console.log('[PWA] Service Worker registered:', this.swRegistration);
                
                // Listen for service worker messages
                navigator.serviceWorker.addEventListener('message', (event) => {
                    this.handleServiceWorkerMessage(event);
                });
                
                // Handle service worker updates
                this.swRegistration.addEventListener('updatefound', () => {
                    const newWorker = this.swRegistration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateAvailable();
                        }
                    });
                });
                
            } catch (error) {
                console.error('[PWA] Service Worker registration failed:', error);
            }
        }
    }

    setupInstallPrompt() {
        // Listen for beforeinstallprompt event
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('[PWA] Install prompt available');
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });

        // Listen for app installed event
        window.addEventListener('appinstalled', () => {
            console.log('[PWA] App installed');
            this.isInstalled = true;
            this.hideInstallButton();
            this.showInstalledMessage();
        });
    }

    showInstallButton() {
        // Create install button if it doesn't exist
        let installBtn = document.getElementById('pwa-install-btn');
        if (!installBtn) {
            installBtn = document.createElement('button');
            installBtn.id = 'pwa-install-btn';
            installBtn.className = 'pwa-install-button';
            installBtn.innerHTML = `
                <i class="fas fa-download"></i>
                <span>Instaliraj aplikaciju</span>
            `;
            installBtn.addEventListener('click', () => this.installApp());
            
            // Add to header or create floating button
            const header = document.querySelector('.header, .navbar');
            if (header) {
                header.appendChild(installBtn);
            } else {
                installBtn.classList.add('floating-install-btn');
                document.body.appendChild(installBtn);
            }
        }
        
        installBtn.style.display = 'flex';
        
        // Add CSS if not exists
        this.addInstallButtonStyles();
    }

    hideInstallButton() {
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.style.display = 'none';
        }
    }

    async installApp() {
        if (!this.deferredPrompt) {
            console.log('[PWA] No install prompt available');
            return;
        }

        // Show install prompt
        this.deferredPrompt.prompt();
        
        // Wait for user choice
        const { outcome } = await this.deferredPrompt.userChoice;
        console.log('[PWA] Install outcome:', outcome);
        
        if (outcome === 'accepted') {
            this.hideInstallButton();
        }
        
        this.deferredPrompt = null;
    }

    checkInstallStatus() {
        // Check if running as PWA
        if (window.matchMedia('(display-mode: standalone)').matches || 
            window.navigator.standalone === true) {
            this.isInstalled = true;
            console.log('[PWA] Running as installed app');
        }
    }

    setupAppUpdates() {
        // Check for updates periodically
        setInterval(() => {
            if (this.swRegistration) {
                this.swRegistration.update();
            }
        }, 60000); // Check every minute
    }

    showUpdateAvailable() {
        // Create update notification
        const updateNotification = document.createElement('div');
        updateNotification.className = 'pwa-update-notification';
        updateNotification.innerHTML = `
            <div class="update-content">
                <i class="fas fa-sync-alt"></i>
                <span>Nova verzija aplikacije je dostupna</span>
                <button onclick="pwaManager.applyUpdate()" class="update-btn">Ažuriraj</button>
                <button onclick="this.parentElement.parentElement.remove()" class="dismiss-btn">×</button>
            </div>
        `;
        
        document.body.appendChild(updateNotification);
        this.addUpdateNotificationStyles();
    }

    applyUpdate() {
        if (this.swRegistration && this.swRegistration.waiting) {
            this.swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
            window.location.reload();
        }
    }

    async setupPushNotifications() {
        if (!('Notification' in window) || !('serviceWorker' in navigator)) {
            console.log('[PWA] Push notifications not supported');
            return;
        }

        // Request notification permission
        if (Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            console.log('[PWA] Notification permission:', permission);
        }

        if (Notification.permission === 'granted' && this.swRegistration) {
            try {
                // Subscribe to push notifications
                const subscription = await this.swRegistration.pushManager.subscribe({
                    userVisibleOnly: true,
                    applicationServerKey: this.urlBase64ToUint8Array(
                        'BEl62iUYgUivxIkv69yViEuiBIa40HI80NM9f4EmgD4kFBqKJrXCLJSuJcQGJPZIiGNLI1CKUB4oRGX4TzfCBsQ'
                    )
                });
                
                console.log('[PWA] Push subscription:', subscription);
                
                // Send subscription to server
                await this.sendSubscriptionToServer(subscription);
                
            } catch (error) {
                console.error('[PWA] Push subscription failed:', error);
            }
        }
    }

    setupBackgroundSync() {
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            // Register background sync for form submissions
            navigator.serviceWorker.ready.then((registration) => {
                // Sync notifications
                registration.sync.register('notification-sync');
                
                // Sync shipments when online
                registration.sync.register('shipment-sync');
                
                console.log('[PWA] Background sync registered');
            });
        }
    }

    handleServiceWorkerMessage(event) {
        const { data } = event;
        
        if (data.type === 'NOTIFICATIONS_UPDATE') {
            this.updateNotificationUI(data.notifications);
        } else if (data.type === 'CACHE_UPDATED') {
            console.log('[PWA] Cache updated');
        }
    }

    updateNotificationUI(notifications) {
        // Update notification badge or UI
        const notificationBadge = document.querySelector('.notification-badge');
        if (notificationBadge && notifications.length > 0) {
            notificationBadge.textContent = notifications.length;
            notificationBadge.style.display = 'block';
        }
    }

    async sendSubscriptionToServer(subscription) {
        try {
            const response = await fetch('/transport/api/push-subscription/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(subscription)
            });
            
            if (response.ok) {
                console.log('[PWA] Subscription sent to server');
            }
        } catch (error) {
            console.error('[PWA] Failed to send subscription:', error);
        }
    }

    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }

    showInstalledMessage() {
        // Show success message
        const message = document.createElement('div');
        message.className = 'pwa-success-message';
        message.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>Aplikacija je uspešno instalirana!</span>
        `;
        document.body.appendChild(message);
        
        setTimeout(() => {
            message.remove();
        }, 3000);
        
        this.addSuccessMessageStyles();
    }

    addInstallButtonStyles() {
        if (document.getElementById('pwa-install-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'pwa-install-styles';
        styles.textContent = `
            .pwa-install-button {
                background: linear-gradient(45deg, #FFD700, #FFC107);
                border: none;
                color: #000;
                font-weight: 600;
                padding: 8px 16px;
                border-radius: 25px;
                display: flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 14px;
                box-shadow: 0 2px 10px rgba(255, 215, 0, 0.3);
            }
            
            .pwa-install-button:hover {
                background: linear-gradient(45deg, #FFC107, #FFB300);
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(255, 215, 0, 0.4);
            }
            
            .floating-install-btn {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 1000;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
        `;
        document.head.appendChild(styles);
    }

    addUpdateNotificationStyles() {
        if (document.getElementById('pwa-update-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'pwa-update-styles';
        styles.textContent = `
            .pwa-update-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                z-index: 1001;
                max-width: 350px;
                animation: slideIn 0.3s ease;
            }
            
            .update-content {
                display: flex;
                align-items: center;
                gap: 10px;
                flex-wrap: wrap;
            }
            
            .update-btn {
                background: #FFD700;
                border: none;
                color: #000;
                padding: 6px 12px;
                border-radius: 15px;
                font-weight: 600;
                cursor: pointer;
                font-size: 12px;
            }
            
            .dismiss-btn {
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                color: #666;
                margin-left: auto;
            }
            
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(styles);
    }

    addSuccessMessageStyles() {
        if (document.getElementById('pwa-success-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'pwa-success-styles';
        styles.textContent = `
            .pwa-success-message {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(46, 204, 113, 0.95);
                color: white;
                padding: 20px 30px;
                border-radius: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
                font-weight: 600;
                z-index: 1002;
                animation: fadeInOut 3s ease;
            }
            
            @keyframes fadeInOut {
                0%, 100% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
                20%, 80% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            }
        `;
        document.head.appendChild(styles);
    }
}

// Initialize PWA Manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.pwaManager = new PWAManager();
});

// Export for global access
window.PWAManager = PWAManager;
