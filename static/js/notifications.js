// Audio Notification System for Tovar Taxi
class AudioNotificationSystem {
    constructor() {
        this.sounds = {
            ping: new Audio('/static/audio/ping.mp3'),
            success: new Audio('/static/audio/success.wav'),
            alert: new Audio('/static/audio/alert.ogg'),
            newOrder: new Audio('/static/audio/ping.mp3'),
            orderAccepted: new Audio('/static/audio/success.wav'),
            orderCompleted: new Audio('/static/audio/success.wav'),
            paymentReceived: new Audio('/static/audio/success.wav'),
            error: new Audio('/static/audio/alert.ogg')
        };
        
        // Preload all sounds
        Object.values(this.sounds).forEach(sound => {
            sound.preload = 'auto';
            sound.volume = 0.7;
        });
        
        this.notificationContainer = null;
        this.createNotificationContainer();
        this.setupEventListeners();
    }
    
    createNotificationContainer() {
        this.notificationContainer = document.createElement('div');
        this.notificationContainer.id = 'notification-container';
        this.notificationContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            pointer-events: none;
        `;
        
        // Responsive design - mobile takes >50% screen, desktop top-right quarter
        const mediaQuery = window.matchMedia('(max-width: 768px)');
        if (mediaQuery.matches) {
            this.notificationContainer.style.cssText += `
                left: 10px;
                right: 10px;
                max-width: none;
                width: calc(100% - 20px);
            `;
        } else {
            this.notificationContainer.style.cssText += `
                width: 25%;
                min-width: 300px;
            `;
        }
        
        document.body.appendChild(this.notificationContainer);
    }
    
    setupEventListeners() {
        // Listen for custom notification events
        document.addEventListener('tovarTaxiNotification', (event) => {
            this.showNotification(event.detail);
        });
        
        // Periodically check for new notifications from server
        setInterval(() => {
            this.checkForNewNotifications();
        }, 10000); // Check every 10 seconds
    }
    
    async checkForNewNotifications() {
        try {
            const response = await fetch('/transport/api/notifications/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                data.notifications.forEach(notification => {
                    if (!notification.is_read) {
                        this.showNotification({
                            type: notification.notification_type,
                            title: notification.title,
                            message: notification.message,
                            sound: notification.sound_file || 'ping',
                            id: notification.id
                        });
                    }
                });
            }
        } catch (error) {
            console.error('Error checking notifications:', error);
        }
    }
    
    playSound(soundName) {
        if (this.sounds[soundName]) {
            try {
                this.sounds[soundName].currentTime = 0;
                this.sounds[soundName].play().catch(e => {
                    console.warn('Could not play notification sound:', e);
                });
            } catch (error) {
                console.warn('Audio playback error:', error);
            }
        }
    }
    
    showNotification({ type = 'info', title, message, sound = 'ping', duration = 5000, id = null, actions = [] }) {
        // Play sound
        this.playSound(sound);
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 15px 20px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            transform: translateX(100%);
            transition: all 0.3s ease;
            pointer-events: auto;
            position: relative;
            overflow: hidden;
        `;
        
        // Add notification content
        notification.innerHTML = `
            <div class="notification-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong style="font-size: 16px;">${this.getNotificationIcon(type)} ${title}</strong>
                <button class="notification-close" style="background: none; border: none; color: white; font-size: 18px; cursor: pointer; padding: 0; width: 20px; height: 20px;">&times;</button>
            </div>
            <div class="notification-message" style="font-size: 14px; line-height: 1.4; margin-bottom: ${actions.length > 0 ? '12px' : '0'};">
                ${message}
            </div>
            ${actions.length > 0 ? `
                <div class="notification-actions" style="display: flex; gap: 8px; flex-wrap: wrap;">
                    ${actions.map(action => `
                        <button class="notification-action" data-action="${action.action}" style="
                            background: rgba(255,255,255,0.2);
                            border: 1px solid rgba(255,255,255,0.3);
                            color: white;
                            padding: 6px 12px;
                            border-radius: 4px;
                            font-size: 12px;
                            cursor: pointer;
                            transition: background 0.2s;
                        " onmouseover="this.style.background='rgba(255,255,255,0.3)'" onmouseout="this.style.background='rgba(255,255,255,0.2)'">
                            ${action.label}
                        </button>
                    `).join('')}
                </div>
            ` : ''}
        `;
        
        // Add progress bar for timed notifications
        if (duration > 0) {
            const progressBar = document.createElement('div');
            progressBar.style.cssText = `
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: rgba(255,255,255,0.5);
                width: 100%;
                transform-origin: left;
                animation: notificationProgress ${duration}ms linear;
            `;
            notification.appendChild(progressBar);
        }
        
        // Add event listeners
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.removeNotification(notification, id);
        });
        
        // Handle action buttons
        notification.querySelectorAll('.notification-action').forEach(button => {
            button.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.handleNotificationAction(action, id);
                this.removeNotification(notification, id);
            });
        });
        
        // Add to container
        this.notificationContainer.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.removeNotification(notification, id);
            }, duration);
        }
        
        // Mark as read on server if it has an ID
        if (id) {
            this.markNotificationAsRead(id);
        }
    }
    
    removeNotification(notification, id = null) {
        notification.style.transform = 'translateX(100%)';
        notification.style.opacity = '0';
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }
    
    async markNotificationAsRead(notificationId) {
        try {
            await fetch(`/transport/api/notifications/${notificationId}/read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                    'Content-Type': 'application/json'
                }
            });
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }
    
    async handleNotificationAction(action, notificationId) {
        try {
            const response = await fetch(`/transport/api/notifications/${notificationId}/action/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ action })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.redirect) {
                    window.location.href = data.redirect;
                }
            }
        } catch (error) {
            console.error('Error handling notification action:', error);
        }
    }
    
    getNotificationColor(type) {
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8',
            cargo: '#6f42c1',
            payment: '#fd7e14'
        };
        return colors[type] || colors.info;
    }
    
    getNotificationIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️',
            cargo: '📦',
            payment: '💳'
        };
        return icons[type] || icons.info;
    }
}

// CSS Animation for progress bar
const style = document.createElement('style');
style.textContent = `
    @keyframes notificationProgress {
        from { transform: scaleX(1); }
        to { transform: scaleX(0); }
    }
    
    .notification:hover .notification-progress {
        animation-play-state: paused;
    }
`;
document.head.appendChild(style);

// Initialize notification system when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.tovarTaxiNotifications = new AudioNotificationSystem();
});

// Utility functions for easy notification triggering
window.showNotification = (options) => {
    if (window.tovarTaxiNotifications) {
        window.tovarTaxiNotifications.showNotification(options);
    }
};

window.playNotificationSound = (soundName) => {
    if (window.tovarTaxiNotifications) {
        window.tovarTaxiNotifications.playSound(soundName);
    }
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AudioNotificationSystem;
}
