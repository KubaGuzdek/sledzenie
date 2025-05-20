/**
 * King Of theBay GPS Tracking Module
 * Handles GPS tracking functionality for participants
 */

// Create namespace
window.gpsTracking = (function() {
    // Private variables
    let watchId = null;
    let isTracking = false;
    let startPosition = null;
    let lastPosition = null;
    let totalDistance = 0;
    let currentSpeed = 0;
    let trackingInterval = null;
    
    // Callbacks
    let positionUpdatedCallback = null;
    let trackingStartedCallback = null;
    let trackingStoppedCallback = null;
    let errorCallback = null;
    
    // Start tracking
    function startTracking() {
        if (isTracking) return false;
        
        console.log('Starting GPS tracking...');
        
        // Check if geolocation is supported
        if (!navigator.geolocation) {
            const error = 'Geolocation is not supported by your browser';
            console.error(error);
            
            if (errorCallback) {
                errorCallback(error);
            }
            
            return false;
        }
        
        // Start watching position
        watchId = navigator.geolocation.watchPosition(
            handlePositionUpdate,
            handlePositionError,
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
        
        // Start tracking interval
        trackingInterval = setInterval(() => {
            // Send position update to server
            if (lastPosition) {
                window.trackingCommunication.sendPositionUpdate(
                    {
                        latitude: lastPosition.coords.latitude,
                        longitude: lastPosition.coords.longitude
                    },
                    currentSpeed,
                    totalDistance
                );
            }
        }, 10000); // Send update every 10 seconds
        
        // Update state
        isTracking = true;
        
        // Trigger callback
        if (trackingStartedCallback) {
            trackingStartedCallback();
        }
        
        return true;
    }
    
    // Stop tracking
    function stopTracking() {
        if (!isTracking) return false;
        
        console.log('Stopping GPS tracking...');
        
        // Stop watching position
        if (watchId !== null) {
            navigator.geolocation.clearWatch(watchId);
            watchId = null;
        }
        
        // Clear tracking interval
        if (trackingInterval !== null) {
            clearInterval(trackingInterval);
            trackingInterval = null;
        }
        
        // Update state
        isTracking = false;
        
        // Trigger callback
        if (trackingStoppedCallback) {
            trackingStoppedCallback();
        }
        
        return true;
    }
    
    // Handle position update
    function handlePositionUpdate(position) {
        console.log('Position update:', position);
        
        // Store position
        if (!startPosition) {
            startPosition = position;
        }
        
        // Calculate distance and speed if we have a previous position
        if (lastPosition) {
            const distance = calculateDistance(
                lastPosition.coords.latitude,
                lastPosition.coords.longitude,
                position.coords.latitude,
                position.coords.longitude
            );
            
            // Add to total distance (in kilometers)
            totalDistance += distance;
            
            // Calculate speed (in km/h)
            const timeDiff = (position.timestamp - lastPosition.timestamp) / 1000; // in seconds
            currentSpeed = (distance / timeDiff) * 3600; // convert to km/h
        }
        
        // Update last position
        lastPosition = position;
        
        // Trigger callback
        if (positionUpdatedCallback) {
            positionUpdatedCallback({
                position: {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                },
                accuracy: position.coords.accuracy,
                speed: currentSpeed,
                distance: totalDistance,
                timestamp: position.timestamp
            });
        }
    }
    
    // Handle position error
    function handlePositionError(error) {
        console.error('Error getting position:', error);
        
        if (errorCallback) {
            errorCallback(error.message);
        }
    }
    
    // Calculate distance between two points using Haversine formula
    function calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Radius of the earth in km
        const dLat = deg2rad(lat2 - lat1);
        const dLon = deg2rad(lon2 - lon1);
        const a =
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        const distance = R * c; // Distance in km
        return distance;
    }
    
    // Convert degrees to radians
    function deg2rad(deg) {
        return deg * (Math.PI / 180);
    }
    
    // Get current position
    function getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject('Geolocation is not supported by your browser');
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    });
                },
                (error) => {
                    reject(error.message);
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        });
    }
    
    // Send SOS alert
    async function sendSOS() {
        console.log('Sending SOS alert...');
        
        try {
            // Get current position
            const position = await getCurrentPosition();
            
            // Send SOS alert to server
            const success = window.trackingCommunication.sendSOS(position);
            
            return success;
        } catch (error) {
            console.error('Error sending SOS alert:', error);
            
            if (errorCallback) {
                errorCallback(error);
            }
            
            return false;
        }
    }
    
    // Reset tracking data
    function resetTrackingData() {
        startPosition = null;
        lastPosition = null;
        totalDistance = 0;
        currentSpeed = 0;
    }
    
    // Register callbacks
    function onPositionUpdated(callback) {
        positionUpdatedCallback = callback;
    }
    
    function onTrackingStarted(callback) {
        trackingStartedCallback = callback;
    }
    
    function onTrackingStopped(callback) {
        trackingStoppedCallback = callback;
    }
    
    function onError(callback) {
        errorCallback = callback;
    }
    
    // Public API
    return {
        startTracking,
        stopTracking,
        getCurrentPosition,
        sendSOS,
        resetTrackingData,
        onPositionUpdated,
        onTrackingStarted,
        onTrackingStopped,
        onError,
        get isTracking() { return isTracking; },
        get currentSpeed() { return currentSpeed; },
        get totalDistance() { return totalDistance; }
    };
})();
