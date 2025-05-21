/**
 * King Of theBay Tracking Communication Module
 * Handles WebSocket communication with the tracking server
 */

// Create namespace
window.trackingCommunication = (function() {
    // Private variables
    let socket = null;
    let isConnected = false;
    let isAuthenticated = false;
    let reconnectAttempts = 0;
    let maxReconnectAttempts = 5;
    let reconnectTimeout = null;
    let pingInterval = null;
    
    // Callbacks
    let connectionStateChangedCallback = null;
    let authSuccessCallback = null;
    let authFailureCallback = null;
    let positionUpdateReceivedCallback = null;
    let raceUpdateReceivedCallback = null;
    let notificationReceivedCallback = null;
    let errorCallback = null;
    
    // Connect to server
    function connect() {
        // Check if already connected
        if (isConnected) return;
        
        // Get server URL - check if we're on PythonAnywhere, Render.com or local development
        let url;
        
        if (window.location.hostname.includes('pythonanywhere.com')) {
            // We're on PythonAnywhere, use WebSocket server on the same domain
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            url = `${protocol}//${window.location.host}`;
            console.log('Using PythonAnywhere WebSocket server');
        } else if (window.location.hostname.includes('onrender.com')) {
            // We're on Render.com, use secure WebSocket with hardcoded URL
            // Render.com uses HTTPS, so we need to use WSS (secure WebSocket)
            url = "wss://sledzenie.onrender.com:10000/ws";
            console.log('Using hardcoded Render.com WebSocket server URL: ' + url);
        } else {
            // Local development
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            url = `${protocol}//${host}`;
        }
        
        console.log(`Connecting to tracking server at ${url}...`);
        
        try {
            // Create WebSocket connection
            socket = new WebSocket(url);
            
            // Set up event handlers
            socket.onopen = handleOpen;
            socket.onmessage = handleMessage;
            socket.onclose = handleClose;
            socket.onerror = handleError;
        } catch (error) {
            console.error('Error connecting to tracking server:', error);
            handleConnectionFailure();
        }
    }
    
    // Disconnect from server
    function disconnect() {
        // Check if connected
        if (!isConnected) return;
        
        console.log('Disconnecting from tracking server...');
        
        // Clear intervals
        clearInterval(pingInterval);
        clearTimeout(reconnectTimeout);
        
        // Close socket
        if (socket) {
            socket.close();
            socket = null;
        }
        
        // Update state
        isConnected = false;
        isAuthenticated = false;
        
        // Trigger callback
        if (connectionStateChangedCallback) {
            connectionStateChangedCallback(false);
        }
    }
    
    // Reconnect to server
    function reconnect() {
        // Check if max attempts reached
        if (reconnectAttempts >= maxReconnectAttempts) {
            console.error('Max reconnect attempts reached');
            return;
        }
        
        // Increment attempts
        reconnectAttempts++;
        
        // Calculate delay (exponential backoff)
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
        
        console.log(`Reconnecting in ${delay / 1000} seconds (attempt ${reconnectAttempts}/${maxReconnectAttempts})...`);
        
        // Set timeout
        reconnectTimeout = setTimeout(() => {
            connect();
        }, delay);
    }
    
    // Handle connection open
    function handleOpen() {
        console.log('Connected to tracking server');
        
        // Update state
        isConnected = true;
        reconnectAttempts = 0;
        
        // Start ping interval
        pingInterval = setInterval(() => {
            if (isConnected) {
                sendPing();
            }
        }, 30000);
        
        // Trigger callback
        if (connectionStateChangedCallback) {
            connectionStateChangedCallback(true);
        }
    }
    
    // Handle connection close
    function handleClose(event) {
        console.log('Disconnected from tracking server:', event.code, event.reason);
        
        // Update state
        isConnected = false;
        isAuthenticated = false;
        
        // Clear ping interval
        clearInterval(pingInterval);
        
        // Trigger callback
        if (connectionStateChangedCallback) {
            connectionStateChangedCallback(false);
        }
        
        // Reconnect if not closed intentionally
        if (event.code !== 1000) {
            handleConnectionFailure();
        }
    }
    
    // Handle connection error
    function handleError(error) {
        console.error('WebSocket error:', error);
        
        // Trigger callback
        if (errorCallback) {
            errorCallback('Connection error');
        }
    }
    
    // Handle connection failure
    function handleConnectionFailure() {
        // Update state
        isConnected = false;
        isAuthenticated = false;
        
        // Clear ping interval
        clearInterval(pingInterval);
        
        // Trigger callback
        if (connectionStateChangedCallback) {
            connectionStateChangedCallback(false);
        }
        
        // Reconnect
        reconnect();
    }
    
    // Handle message
    function handleMessage(event) {
        try {
            // Parse message
            const message = JSON.parse(event.data);
            
            console.log('Received message:', message);
            
            // Handle message based on type
            switch (message.type) {
                case 'connection_established':
                    console.log('Connection established:', message.data.message);
                    break;
                
                case 'auth_success':
                    handleAuthSuccess(message.data);
                    break;
                
                case 'auth_failure':
                    handleAuthFailure(message.data.message);
                    break;
                
                case 'participant_position':
                    handlePositionUpdate(message.data);
                    break;
                
                case 'race_update':
                    handleRaceUpdate(message.data);
                    break;
                
                case 'notification':
                    handleNotification(message.data);
                    break;
                
                case 'sos_confirmation':
                    console.log('SOS confirmation:', message.data.message);
                    break;
                
                case 'error':
                    handleServerError(message.data.message);
                    break;
                
                case 'pong':
                    // Pong received, connection is alive
                    break;
                
                default:
                    console.log('Unknown message type:', message.type);
            }
        } catch (error) {
            console.error('Error handling message:', error);
        }
    }
    
    // Handle authentication success
    function handleAuthSuccess(data) {
        console.log('Authentication successful:', data);
        
        // Update state
        isAuthenticated = true;
        
        // Trigger callback
        if (authSuccessCallback) {
            authSuccessCallback(data);
        }
    }
    
    // Handle authentication failure
    function handleAuthFailure(message) {
        console.error('Authentication failed:', message);
        
        // Update state
        isAuthenticated = false;
        
        // Trigger callback
        if (authFailureCallback) {
            authFailureCallback(message);
        }
    }
    
    // Handle position update
    function handlePositionUpdate(data) {
        // Trigger callback
        if (positionUpdateReceivedCallback) {
            positionUpdateReceivedCallback(data);
        }
    }
    
    // Handle race update
    function handleRaceUpdate(data) {
        // Trigger callback
        if (raceUpdateReceivedCallback) {
            raceUpdateReceivedCallback(data);
        }
    }
    
    // Handle notification
    function handleNotification(data) {
        // Trigger callback
        if (notificationReceivedCallback) {
            notificationReceivedCallback(data);
        }
    }
    
    // Handle server error
    function handleServerError(message) {
        console.error('Server error:', message);
        
        // Trigger callback
        if (errorCallback) {
            errorCallback(message);
        }
    }
    
    // Send message
    function sendMessage(type, data = {}) {
        // Check if connected
        if (!isConnected) {
            console.error('Not connected to server');
            return false;
        }
        
        try {
            // Create message
            const message = {
                type,
                ...data
            };
            
            // Send message
            socket.send(JSON.stringify(message));
            
            return true;
        } catch (error) {
            console.error('Error sending message:', error);
            return false;
        }
    }
    
    // Send ping
    function sendPing() {
        return sendMessage('ping', { timestamp: Date.now() });
    }
    
    // Authenticate
    function authenticate(token) {
        return sendMessage('auth', { token });
    }
    
    // Send position update
    function sendPositionUpdate(position, speed, distance) {
        return sendMessage('position_update', { position, speed, distance });
    }
    
    // Send SOS alert
    function sendSOS(position) {
        return sendMessage('sos', { position });
    }
    
    // Register callbacks
    function onConnectionStateChanged(callback) {
        connectionStateChangedCallback = callback;
    }
    
    function onAuthSuccess(callback) {
        authSuccessCallback = callback;
    }
    
    function onAuthFailure(callback) {
        authFailureCallback = callback;
    }
    
    function onPositionUpdateReceived(callback) {
        positionUpdateReceivedCallback = callback;
    }
    
    function onRaceUpdateReceived(callback) {
        raceUpdateReceivedCallback = callback;
    }
    
    function onNotificationReceived(callback) {
        notificationReceivedCallback = callback;
    }
    
    function onError(callback) {
        errorCallback = callback;
    }
    
    // Public API
    return {
        connect,
        disconnect,
        authenticate,
        sendPositionUpdate,
        sendSOS,
        onConnectionStateChanged,
        onAuthSuccess,
        onAuthFailure,
        onPositionUpdateReceived,
        onRaceUpdateReceived,
        onNotificationReceived,
        onError,
        get isConnected() { return isConnected; },
        get isAuthenticated() { return isAuthenticated; }
    };
})();
