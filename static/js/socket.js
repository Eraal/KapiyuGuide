// base_socket.js - Core WebSocket connection and management

class BaseSocketManager {
    constructor(options = {}) {
        this.options = {
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: Infinity,
            timeout: 20000,
            autoConnect: true,
            ...options
        };
        
        this.socket = null;
        this.isConnected = false;
        this.eventHandlers = {};
        this._createConnectionIndicator();
        this._createNotificationContainer();
    }

    initialize() {
        return new Promise((resolve, reject) => {
            if (typeof io === 'undefined') {
                console.log('Loading Socket.IO library...');
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.6.1/socket.io.min.js';
                script.onload = () => {
                    console.log('Socket.IO loaded successfully');
                    this._connect(resolve, reject);
                };
                script.onerror = () => {
                    const error = new Error('Failed to load Socket.IO');
                    console.error(error);
                    this._showNotification('Connection Error', 'Failed to establish real-time connection.', 'error');
                    reject(error);
                };
                document.head.appendChild(script);
            } else {
                console.log('Socket.IO already loaded');
                this._connect(resolve, reject);
            }
        });
    }

    _connect(resolve, reject) {
        try {
            // Initialize Socket.IO connection with options
            this.socket = io.connect(window.location.origin, this.options);

            // Set up core connection events
            this.socket.on('connect', () => {
                console.log('Connected to WebSocket server with ID:', this.socket.id);
                
                this.isConnected = true;
                this._updateConnectionIndicator(true);
                
                // Register any stored event handlers
                this._registerStoredHandlers();
                
                // Emit connection event for other components
                const event = new CustomEvent('socket:connected', {
                    detail: { socketId: this.socket.id }
                });
                document.dispatchEvent(event);
                
                // Explicitly ping the server to verify connection health
                this.socket.emit('ping_server', { timestamp: new Date().toISOString() });
                
                resolve(this.socket);
            });

            this.socket.on('connect_error', (error) => {
                console.error('Connection error:', error);
                this._showNotification('Connection Error', 'Failed to connect. Will retry...', 'error');
            });

            this.socket.on('connect_timeout', () => {
                console.error('Connection timeout');
                this._showNotification('Connection Timeout', 'Connection timed out. Will retry...', 'warning');
            });

            this.socket.on('disconnect', (reason) => {
                console.log('Disconnected from WebSocket server. Reason:', reason);
                this.isConnected = false;
                this._updateConnectionIndicator(false);

                // Show a notification only for unexpected disconnects
                if (reason !== 'io client disconnect') {
                    this._showNotification('Disconnected', 'Real-time updates paused. Reconnecting...', 'warning');
                }
            });
            
            // Common pong handler
            this.socket.on('pong_server', (data) => {
                console.log('Server pong received:', data);
            });
            
            // Add event handlers for the notification system from models
            this._setupApplicationHandlers();
            
        } catch (error) {
            console.error('Error initializing Socket.IO:', error);
            this._showNotification('WebSocket Error', 'Could not initialize real-time updates', 'error');
            reject(error);
        }
    }

    on(event, callback) {
        if (!this.socket) {
            // Store event handlers to be registered once socket is connected
            this.eventHandlers[event] = this.eventHandlers[event] || [];
            this.eventHandlers[event].push(callback);
            return;
        }
        
        this.socket.on(event, callback);
    }

    emit(event, data) {
        if (!this.socket || !this.isConnected) {
            console.warn(`Cannot emit '${event}' - socket not connected`);
            return false;
        }
        
        this.socket.emit(event, data);
        return true;
    }

    _registerStoredHandlers() {
        if (!this.socket) return;
        
        Object.keys(this.eventHandlers).forEach(event => {
            this.eventHandlers[event].forEach(callback => {
                this.socket.on(event, callback);
            });
        });
    }

    _setupApplicationHandlers() {
        // Setup handlers based on the application models
        
        // Notification handler
        this.on('notification', (data) => {
            this._showNotification(data.title, data.message, data.type || 'info');
            
            // Update notification count UI if exists
            this._updateNotificationCount();
        });
        
        // Inquiry message handler
        this.on('new_inquiry_message', (data) => {
            // Handle new inquiry messages
            console.log('New inquiry message received:', data);
            
            // Show notification if not on the related inquiry page
            const currentPath = window.location.pathname;
            if (!currentPath.includes(`/inquiry/${data.inquiry_id}`)) {
                this._showNotification('New Message', `You have a new message in inquiry #${data.inquiry_id}`, 'info');
            }
            
            // Dispatch custom event for inquiry message components
            const event = new CustomEvent('inquiry:new_message', {
                detail: data
            });
            document.dispatchEvent(event);
        });
        
        // Counseling session updates
        this.on('counseling_session_update', (data) => {
            console.log('Counseling session update:', data);
            
            this._showNotification('Counseling Session', 
                `Counseling session #${data.id} status changed to ${data.status}`, 
                'info');
                
            // Dispatch custom event for counseling components
            const event = new CustomEvent('counseling:update', {
                detail: data
            });
            document.dispatchEvent(event);
        });
        
        // Announcement notifications
        this.on('new_announcement', (data) => {
            console.log('New announcement received:', data);
            this._showNotification('New Announcement', data.title, 'info');
        });
    }

    _updateConnectionIndicator(isConnected) {
        // Create indicator if it doesn't exist
        if (!document.getElementById('connection-status')) {
            this._createConnectionIndicator();
        }
        
        const statusIndicator = document.getElementById('connection-status');
        const statusText = statusIndicator.querySelector('.connection-status-text');
        const iconContainer = statusIndicator.querySelector('.inline-flex');
        const icon = statusIndicator.querySelector('svg');
        
        if (isConnected) {
            // Update classes for connected state
            statusIndicator.classList.remove('bg-red-50', 'text-red-800', 'border-red-200');
            statusIndicator.classList.add('bg-green-50', 'text-green-800', 'border-green-200');
            
            iconContainer.classList.remove('bg-red-100', 'text-red-500');
            iconContainer.classList.add('bg-green-100', 'text-green-500');
            
            // Update icon to checkmark
            icon.innerHTML = '<path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>';
            
            // Update text
            statusText.textContent = 'WebSocket Connected';
        } else {
            // Update classes for disconnected state
            statusIndicator.classList.remove('bg-green-50', 'text-green-800', 'border-green-200');
            statusIndicator.classList.add('bg-red-50', 'text-red-800', 'border-red-200');
            
            iconContainer.classList.remove('bg-green-100', 'text-green-500');
            iconContainer.classList.add('bg-red-100', 'text-red-500');
            
            // Update icon to X
            icon.innerHTML = '<path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>';
            
            // Update text
            statusText.textContent = 'WebSocket Disconnected';
        }
        
        // Update tooltip
        statusIndicator.setAttribute('title', isConnected ? 
            'Connected to real-time updates' : 
            'Disconnected from real-time updates');
    }

    _createConnectionIndicator() {
        // Check if indicator already exists
        if (document.getElementById('connection-status')) return;
        
        const indicator = document.createElement('div');
        indicator.id = 'connection-status';
        indicator.className = 'fixed bottom-4 left-4 z-50 flex items-center p-2 px-3 rounded-lg shadow-md border transition-all duration-300 transform opacity-0 translate-y-2 bg-red-50 text-red-800 border-red-200';
        
        indicator.innerHTML = `
            <div class="inline-flex items-center justify-center flex-shrink-0 w-6 h-6 rounded-full bg-red-100 text-red-500 mr-2">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                </svg>
            </div>
            <span class="text-xs font-medium connection-status-text">WebSocket Disconnected</span>
        `;
        
        // Create toggle button
        const toggleButton = document.createElement('button');
        toggleButton.className = 'ml-2 text-xs opacity-70 hover:opacity-100';
        toggleButton.textContent = 'Hide';
        toggleButton.setAttribute('title', 'Toggle visibility');
        
        // Add click event to toggle button
        toggleButton.addEventListener('click', () => {
            const statusText = indicator.querySelector('.connection-status-text');
            const isCompact = indicator.classList.contains('compact-mode');
            
            if (isCompact) {
                // Switch to full mode
                indicator.classList.remove('compact-mode');
                statusText.style.display = 'inline';
                toggleButton.textContent = 'Hide';
                // Adjust padding
                indicator.classList.remove('p-1');
                indicator.classList.add('p-2', 'px-3');
            } else {
                // Switch to compact mode
                indicator.classList.add('compact-mode');
                statusText.style.display = 'none';
                toggleButton.textContent = 'Show';
                // Adjust padding
                indicator.classList.remove('p-2', 'px-3');
                indicator.classList.add('p-1');
            }
        });
        
        // Add toggle button to indicator
        indicator.appendChild(toggleButton);
        
        document.body.appendChild(indicator);
        
        // Store current connection state in data attribute
        indicator.setAttribute('data-connected', 'false');
        
        // Animate in
        setTimeout(() => {
            indicator.classList.remove('opacity-0', 'translate-y-2');
        }, 10);
        
        return indicator;
    }
    
    _createNotificationContainer() {
        if (document.getElementById('toast-container')) return;
        
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed top-4 right-4 z-50 flex flex-col gap-2';
        document.body.appendChild(container);
    }

    _showNotification(title, message, type = 'info') {
        let container = document.getElementById('toast-container');
        if (!container) {
            this._createNotificationContainer();
            container = document.getElementById('toast-container');
        }
        
        const toast = document.createElement('div');

        toast.className = 'flex items-center p-4 mb-4 rounded-lg shadow-lg max-w-xs transform transition-all duration-300 opacity-0 translate-x-4 border-l-4 backdrop-filter backdrop-blur-sm';
        
        // Set icon and colors based on notification type
        let iconSvg, bgColor, textColor, borderColor;
        switch (type) {
            case 'error':
                iconSvg = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                          </svg>`;
                bgColor = 'bg-red-50';
                textColor = 'text-red-700';
                borderColor = 'border-red-500';
                break;
            case 'warning':
                iconSvg = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                          </svg>`;
                bgColor = 'bg-yellow-50';
                textColor = 'text-yellow-700';
                borderColor = 'border-yellow-500';
                break;
            case 'success':
                iconSvg = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                          </svg>`;
                bgColor = 'bg-green-50';
                textColor = 'text-green-700';
                borderColor = 'border-green-500';
                break;
            default: // info
                iconSvg = `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
                          </svg>`;
                bgColor = 'bg-blue-50';
                textColor = 'text-blue-700';
                borderColor = 'border-blue-500';
                break;
        }
        
        // Add styling classes
        toast.classList.add(bgColor, textColor, borderColor);
        
        // Create enhanced content with icon
        toast.innerHTML = `
            <div class="flex-shrink-0 mr-3">
                ${iconSvg}
            </div>
            <div class="flex-grow mr-2">
                <h4 class="font-semibold">${title}</h4>
                <p class="text-sm opacity-90">${message}</p>
            </div>
            <button class="flex-shrink-0 p-1 rounded-full hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-400 transition-colors">
                <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;
        
        // Add to container
        container.appendChild(toast);
        
        // Animate in with a slight delay
        setTimeout(() => {
            toast.classList.remove('opacity-0', 'translate-x-4');
        }, 10);
        
        // Add close button functionality
        const closeBtn = toast.querySelector('button');
        closeBtn.addEventListener('click', () => {
            toast.classList.add('opacity-0', 'translate-x-4');
            setTimeout(() => toast.remove(), 300);
        });
        
        // Add hover effect to pause auto-dismiss
        let dismissTimeout;
        const startDismissTimer = () => {
            dismissTimeout = setTimeout(() => {
                if (toast.parentNode) {
                    toast.classList.add('opacity-0', 'translate-x-4');
                    setTimeout(() => toast.remove(), 300);
                }
            }, 5000);
        };
        
        toast.addEventListener('mouseenter', () => {
            clearTimeout(dismissTimeout);
        });
        
        toast.addEventListener('mouseleave', () => {
            startDismissTimer();
        });
        
        // Start auto-dismiss timer
        startDismissTimer();
        
        // Also log to console
        console.log(`${type.toUpperCase()}: ${title} - ${message}`);
    }
    
    _updateNotificationCount() {
        // Update notification badge if exists
        const badge = document.getElementById('notification-badge');
        if (badge) {
            // Fetch current count from API or increment
            fetch('/api/notifications/unread-count')
                .then(response => response.json())
                .then(data => {
                    if (data.count > 0) {
                        badge.textContent = data.count;
                        badge.classList.remove('hidden');
                    } else {
                        badge.classList.add('hidden');
                    }
                })
                .catch(error => console.error('Error updating notification count:', error));
        }
    }
}

window.socketManager = new BaseSocketManager();

document.addEventListener('DOMContentLoaded', () => {
    if (window.socketManager) {
        window.socketManager.initialize()
            .then(() => {
                console.log('WebSocket initialized successfully.');
                
            })
            .catch((error) => {
                console.error('WebSocket initialization failed:', error);
            });
    }
});