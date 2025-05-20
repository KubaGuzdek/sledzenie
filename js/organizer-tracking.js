/**
 * King Of theBay Organizer Tracking Module
 * Handles tracking functionality for the organizer view
 */

// Create namespace
window.organizerTracking = (function() {
    // Private variables
    let map = null;
    let markers = {};
    let participants = [];
    let activeRace = null;
    let sosAlerts = [];
    let selectedParticipant = null;
    
    // Callbacks
    let participantsUpdatedCallback = null;
    let raceUpdatedCallback = null;
    let sosAlertCallback = null;
    let participantSelectedCallback = null;
    
    // Initialize
    function initialize() {
        console.log('Initializing organizer tracking...');
        
        // Set up tracking communication callbacks
        setupTrackingCommunication();
        
        // Load participants
        loadParticipants();
    }
    
    // Set up tracking communication callbacks
    function setupTrackingCommunication() {
        // Position update
        window.trackingCommunication.onPositionUpdateReceived((data) => {
            updateParticipantPosition(data);
        });
        
        // Race update
        window.trackingCommunication.onRaceUpdateReceived((data) => {
            updateRace(data);
        });
        
        // SOS alert
        window.trackingCommunication.onNotificationReceived((data) => {
            if (data.type === 'sos') {
                handleSOSAlert(data);
            }
        });
    }
    
    // Initialize map
    function initializeMap(mapElement) {
        console.log('Initializing map...');
        
        // Store map element
        map = {
            element: mapElement,
            center: { latitude: 54.352, longitude: 18.646 }, // Gdańsk, Poland
            zoom: 12
        };
        
        // In a real implementation, this would initialize a mapping library like Google Maps or Leaflet
        // For this demo, we'll just show a placeholder
        
        // Create map placeholder
        mapElement.innerHTML = `
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; color: #5f6368;">
                <i class="fas fa-map-marker-alt" style="font-size: 48px; margin-bottom: 20px;"></i>
                <h3>Mapa śledzenia</h3>
                <p>W rzeczywistej implementacji, tutaj byłaby mapa Google Maps lub Leaflet</p>
            </div>
        `;
        
        // Add markers for existing participants
        participants.forEach(participant => {
            if (participant.position) {
                addMarker(participant);
            }
        });
    }
    
    // Load participants
    async function loadParticipants() {
        try {
            const token = localStorage.getItem('authToken');
            
            if (!token) {
                console.error('No auth token found');
                return;
            }
            
            // Fetch participants from API
            const response = await fetch('/api/participants', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to load participants');
            }
            
            // Parse response
            const data = await response.json();
            
            // Update participants
            participants = data;
            
            // Trigger callback
            if (participantsUpdatedCallback) {
                participantsUpdatedCallback(participants);
            }
            
            console.log('Participants loaded:', participants);
        } catch (error) {
            console.error('Error loading participants:', error);
        }
    }
    
    // Update participant position
    function updateParticipantPosition(data) {
        // Find participant
        const participant = participants.find(p => p.id === data.participantId);
        
        if (!participant) {
            console.error('Participant not found:', data.participantId);
            return;
        }
        
        // Update participant data
        participant.position = data.position;
        participant.speed = data.speed;
        participant.distance = data.distance;
        participant.lastUpdate = data.timestamp;
        participant.isActive = true;
        
        // Update marker
        updateMarker(participant);
        
        // Update selected participant details if this is the selected one
        if (selectedParticipant === participant.id) {
            if (participantSelectedCallback) {
                participantSelectedCallback(participant);
            }
        }
        
        // Trigger callback
        if (participantsUpdatedCallback) {
            participantsUpdatedCallback(participants);
        }
    }
    
    // Add marker
    function addMarker(participant) {
        // Check if map is initialized
        if (!map) {
            console.error('Map not initialized');
            return;
        }
        
        // Check if participant has position
        if (!participant.position) {
            return;
        }
        
        // In a real implementation, this would add a marker to the map
        // For this demo, we'll just log it
        console.log('Adding marker for participant:', participant.name, participant.position);
        
        // Store marker
        markers[participant.id] = {
            position: participant.position,
            color: participant.trackingColor || '#1a73e8'
        };
    }
    
    // Update marker
    function updateMarker(participant) {
        // Check if map is initialized
        if (!map) {
            console.error('Map not initialized');
            return;
        }
        
        // Check if participant has position
        if (!participant.position) {
            return;
        }
        
        // Check if marker exists
        if (!markers[participant.id]) {
            // Add marker
            addMarker(participant);
            return;
        }
        
        // In a real implementation, this would update the marker position
        // For this demo, we'll just log it
        console.log('Updating marker for participant:', participant.name, participant.position);
        
        // Update marker
        markers[participant.id].position = participant.position;
    }
    
    // Remove marker
    function removeMarker(participantId) {
        // Check if map is initialized
        if (!map) {
            console.error('Map not initialized');
            return;
        }
        
        // Check if marker exists
        if (!markers[participantId]) {
            return;
        }
        
        // In a real implementation, this would remove the marker from the map
        // For this demo, we'll just log it
        console.log('Removing marker for participant:', participantId);
        
        // Remove marker
        delete markers[participantId];
    }
    
    // Center map on position
    function centerMapOnPosition(position) {
        // Check if map is initialized
        if (!map) {
            console.error('Map not initialized');
            return;
        }
        
        // In a real implementation, this would center the map on the position
        // For this demo, we'll just log it
        console.log('Centering map on position:', position);
        
        // Update map center
        map.center = position;
    }
    
    // Select participant
    function selectParticipant(participantId) {
        // Check if already selected
        if (selectedParticipant === participantId) {
            return;
        }
        
        // Update selected participant
        selectedParticipant = participantId;
        
        // Find participant
        const participant = participants.find(p => p.id === participantId);
        
        if (!participant) {
            console.error('Participant not found:', participantId);
            return;
        }
        
        // Center map on participant
        if (participant.position) {
            centerMapOnPosition(participant.position);
        }
        
        // Trigger callback
        if (participantSelectedCallback) {
            participantSelectedCallback(participant);
        }
        
        console.log('Selected participant:', participant.name);
    }
    
    // Create race
    async function createRace(name) {
        try {
            const token = localStorage.getItem('authToken');
            
            if (!token) {
                console.error('No auth token found');
                return false;
            }
            
            // Create race via API
            const response = await fetch('/api/races', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    name,
                    status: 'pending'
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to create race');
            }
            
            // Parse response
            const data = await response.json();
            
            // Update active race
            activeRace = data;
            
            // Trigger callback
            if (raceUpdatedCallback) {
                raceUpdatedCallback(activeRace);
            }
            
            console.log('Race created:', activeRace);
            
            return true;
        } catch (error) {
            console.error('Error creating race:', error);
            return false;
        }
    }
    
    // Start race
    async function startRace() {
        try {
            // Check if there's an active race
            if (!activeRace) {
                console.error('No active race');
                return false;
            }
            
            const token = localStorage.getItem('authToken');
            
            if (!token) {
                console.error('No auth token found');
                return false;
            }
            
            // Start race via API
            const response = await fetch(`/api/races/${activeRace.id}/resume`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to start race');
            }
            
            // Parse response
            const data = await response.json();
            
            // Update active race
            activeRace = data;
            
            // Trigger callback
            if (raceUpdatedCallback) {
                raceUpdatedCallback(activeRace);
            }
            
            console.log('Race started:', activeRace);
            
            return true;
        } catch (error) {
            console.error('Error starting race:', error);
            return false;
        }
    }
    
    // Pause race
    async function pauseRace() {
        try {
            // Check if there's an active race
            if (!activeRace) {
                console.error('No active race');
                return false;
            }
            
            const token = localStorage.getItem('authToken');
            
            if (!token) {
                console.error('No auth token found');
                return false;
            }
            
            // Pause race via API
            const response = await fetch(`/api/races/${activeRace.id}/pause`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to pause race');
            }
            
            // Parse response
            const data = await response.json();
            
            // Update active race
            activeRace = data;
            
            // Trigger callback
            if (raceUpdatedCallback) {
                raceUpdatedCallback(activeRace);
            }
            
            console.log('Race paused:', activeRace);
            
            return true;
        } catch (error) {
            console.error('Error pausing race:', error);
            return false;
        }
    }
    
    // End race
    async function endRace() {
        try {
            // Check if there's an active race
            if (!activeRace) {
                console.error('No active race');
                return false;
            }
            
            const token = localStorage.getItem('authToken');
            
            if (!token) {
                console.error('No auth token found');
                return false;
            }
            
            // End race via API
            const response = await fetch(`/api/races/${activeRace.id}/end`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to end race');
            }
            
            // Parse response
            const data = await response.json();
            
            // Update active race
            activeRace = data;
            
            // Trigger callback
            if (raceUpdatedCallback) {
                raceUpdatedCallback(activeRace);
            }
            
            console.log('Race ended:', activeRace);
            
            return true;
        } catch (error) {
            console.error('Error ending race:', error);
            return false;
        }
    }
    
    // Update race
    function updateRace(data) {
        // Update active race
        activeRace = data;
        
        // Trigger callback
        if (raceUpdatedCallback) {
            raceUpdatedCallback(activeRace);
        }
    }
    
    // Handle SOS alert
    function handleSOSAlert(data) {
        // Add to SOS alerts
        sosAlerts.push(data);
        
        // Trigger callback
        if (sosAlertCallback) {
            sosAlertCallback(sosAlerts);
        }
        
        console.log('SOS alert received:', data);
    }
    
    // Resolve SOS alert
    async function resolveSOSAlert(alertId) {
        try {
            const token = localStorage.getItem('authToken');
            
            if (!token) {
                console.error('No auth token found');
                return false;
            }
            
            // Resolve SOS alert via API
            const response = await fetch(`/api/sos/${alertId}/resolve`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('Failed to resolve SOS alert');
            }
            
            // Parse response
            const data = await response.json();
            
            // Update SOS alert
            const alertIndex = sosAlerts.findIndex(a => a.id === alertId);
            
            if (alertIndex !== -1) {
                sosAlerts[alertIndex] = data;
            }
            
            // Trigger callback
            if (sosAlertCallback) {
                sosAlertCallback(sosAlerts);
            }
            
            console.log('SOS alert resolved:', data);
            
            return true;
        } catch (error) {
            console.error('Error resolving SOS alert:', error);
            return false;
        }
    }
    
    // Send notification
    async function sendNotification(title, message, type, recipient) {
        try {
            const token = localStorage.getItem('authToken');
            
            if (!token) {
                console.error('No auth token found');
                return false;
            }
            
            // Send notification via API
            const response = await fetch('/api/notifications', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    title,
                    message,
                    type,
                    recipient
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to send notification');
            }
            
            console.log('Notification sent:', title, message, type, recipient);
            
            return true;
        } catch (error) {
            console.error('Error sending notification:', error);
            return false;
        }
    }
    
    // Register callbacks
    function onParticipantsUpdated(callback) {
        participantsUpdatedCallback = callback;
    }
    
    function onRaceUpdated(callback) {
        raceUpdatedCallback = callback;
    }
    
    function onSOSAlert(callback) {
        sosAlertCallback = callback;
    }
    
    function onParticipantSelected(callback) {
        participantSelectedCallback = callback;
    }
    
    // Public API
    return {
        initialize,
        initializeMap,
        selectParticipant,
        createRace,
        startRace,
        pauseRace,
        endRace,
        resolveSOSAlert,
        sendNotification,
        centerMapOnPosition,
        onParticipantsUpdated,
        onRaceUpdated,
        onSOSAlert,
        onParticipantSelected,
        get participants() { return participants; },
        get activeRace() { return activeRace; },
        get sosAlerts() { return sosAlerts; },
        get selectedParticipant() { return selectedParticipant; }
    };
})();
