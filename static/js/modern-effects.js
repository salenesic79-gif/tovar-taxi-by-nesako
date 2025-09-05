// TOVAR TAXI - MODERNI JAVASCRIPT EFEKTI

document.addEventListener('DOMContentLoaded', function() {
    
    // Intersection Observer za animacije na scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe sve elemente sa animation klasama
    document.querySelectorAll('.card, .freight-item, .dashboard-card').forEach(el => {
        observer.observe(el);
    });

    // Smooth scrolling za sve linkove
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Loading states za forme
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="loading-spinner"></span> Šalje se...';
                submitBtn.disabled = true;
            }
        });
    });

    // Real-time validacija formi
    document.querySelectorAll('input[required], select[required]').forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                validateField(this);
            }
        });
    });

    function validateField(field) {
        const isValid = field.checkValidity();
        field.classList.toggle('is-valid', isValid);
        field.classList.toggle('is-invalid', !isValid);
        
        // Dodaj custom poruke
        let feedback = field.parentNode.querySelector('.invalid-feedback');
        if (!feedback && !isValid) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentNode.appendChild(feedback);
        }
        
        if (feedback) {
            if (!isValid) {
                feedback.textContent = getValidationMessage(field);
                feedback.style.display = 'block';
            } else {
                feedback.style.display = 'none';
            }
        }
    }

    function getValidationMessage(field) {
        if (field.validity.valueMissing) {
            return 'Ovo polje je obavezno.';
        }
        if (field.validity.typeMismatch) {
            return 'Molimo unesite validnu vrednost.';
        }
        if (field.validity.patternMismatch) {
            return 'Format nije ispravan.';
        }
        return 'Molimo proverite unos.';
    }

    // Parallax efekat za hero sekcije
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.parallax');
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });

    // Auto-hide alerts
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });

    // Tooltip initialization
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Progressive enhancement za WebSocket
    if ('WebSocket' in window) {
        initializeWebSocket();
    }

    function initializeWebSocket() {
        // Real-time notifikacije
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`;
        
        try {
            const socket = new WebSocket(wsUrl);
            
            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                showNotification(data.message, data.type || 'info');
            };
            
            socket.onerror = function(error) {
                console.log('WebSocket error:', error);
            };
        } catch (error) {
            console.log('WebSocket not available:', error);
        }
    }

    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification-toast`;
        notification.innerHTML = `
            <strong>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</strong>
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        // Dodaj na vrh stranice
        document.body.insertBefore(notification, document.body.firstChild);
        
        // Auto remove
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }

    // Lazy loading za slike
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                if (perfData.loadEventEnd - perfData.loadEventStart > 3000) {
                    console.warn('Slow page load detected');
                }
            }, 0);
        });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl+/ za help
        if (e.ctrlKey && e.key === '/') {
            e.preventDefault();
            showKeyboardShortcuts();
        }
        
        // Escape za zatvaranje modala
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(modal => {
                if (typeof bootstrap !== 'undefined') {
                    bootstrap.Modal.getInstance(modal)?.hide();
                }
            });
        }
    });

    function showKeyboardShortcuts() {
        const shortcuts = `
            <div class="modal fade" id="shortcutsModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">⌨️ Prečice na tastaturi</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <ul class="list-unstyled">
                                <li><kbd>Ctrl</kbd> + <kbd>/</kbd> - Prikaži prečice</li>
                                <li><kbd>Esc</kbd> - Zatvori modal</li>
                                <li><kbd>Tab</kbd> - Navigacija kroz elemente</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        if (!document.getElementById('shortcutsModal')) {
            document.body.insertAdjacentHTML('beforeend', shortcuts);
        }
        
        if (typeof bootstrap !== 'undefined') {
            new bootstrap.Modal(document.getElementById('shortcutsModal')).show();
        }
    }

    // Debug Popup System
    function showDebugPopup(title, message, type = 'error') {
        // Remove existing popup if any
        const existingPopup = document.querySelector('.debug-popup-overlay');
        if (existingPopup) {
            existingPopup.remove();
        }

        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'debug-popup-overlay';

        // Create popup
        const popup = document.createElement('div');
        popup.className = `debug-popup error-${type}`;
        
        popup.innerHTML = `
            <div class="debug-popup-title">${title}</div>
            <div class="debug-popup-message">${message}</div>
            <button class="debug-popup-close" onclick="closeDebugPopup()">U redu</button>
        `;

        overlay.appendChild(popup);
        document.body.appendChild(overlay);

        // Close on overlay click
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                closeDebugPopup();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeDebugPopup();
            }
        });
    }

    function closeDebugPopup() {
        const overlay = document.querySelector('.debug-popup-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    // Auto-detect common errors and show popup
    // Check for Django form errors
    const errorElements = document.querySelectorAll('.text-danger, .errorlist, .alert-danger');
    if (errorElements.length > 0) {
        let errorMessage = '';
        errorElements.forEach(element => {
            const text = element.textContent.trim();
            if (text) {
                errorMessage += text + '\n';
            }
        });
        
        if (errorMessage) {
            // Determine error type based on content
            let errorType = 'validation';
            let title = 'Greška u validaciji';
            
            if (errorMessage.toLowerCase().includes('username') || errorMessage.toLowerCase().includes('korisničko ime')) {
                errorType = 'username';
                title = 'Greška sa korisničkim imenom';
            } else if (errorMessage.toLowerCase().includes('connection') || errorMessage.toLowerCase().includes('konekcija')) {
                errorType = 'connection';
                title = 'Greška konekcije';
            } else if (errorMessage.toLowerCase().includes('server') || errorMessage.toLowerCase().includes('500')) {
                errorType = 'server';
                title = 'Greška servera';
            }
            
            showDebugPopup(title, errorMessage.trim(), errorType);
        }
    }
    
    // Check for network errors
    window.addEventListener('offline', function() {
        showDebugPopup('Nema internet konekcije', 'Proverite vašu internet konekciju i pokušajte ponovo.', 'connection');
    });
    
    // Check for JavaScript errors
    window.addEventListener('error', function(e) {
        showDebugPopup('JavaScript greška', 'Dogodila se neočekivana greška. Molimo osvežite stranicu.', 'server');
    });
});

// CSS dodatak za notifikacije
const notificationStyles = `
<style>
.notification-toast {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    min-width: 300px;
    animation: slideInRight 0.3s ease-out;
}

.animate-in {
    animation: slideInUp 0.6s ease-out;
}

.lazy {
    opacity: 0;
    transition: opacity 0.3s;
}

.parallax {
    will-change: transform;
}

@media (max-width: 768px) {
    .notification-toast {
        right: 10px;
        left: 10px;
        min-width: auto;
    }
}

.debug-popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}

.debug-popup {
    background-color: #fff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
    max-width: 500px;
}

.debug-popup-title {
    font-weight: bold;
    font-size: 18px;
    margin-bottom: 10px;
}

.debug-popup-message {
    margin-bottom: 20px;
}

.debug-popup-close {
    background-color: #007bff;
    color: #fff;
    border: none;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
}

.debug-popup-close:hover {
    background-color: #0056b3;
}
</style>
`;

document.head.insertAdjacentHTML('beforeend', notificationStyles);
