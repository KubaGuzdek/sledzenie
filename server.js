/**
 * King Of theBay GPS Tracking Server
 * This server handles WebSocket communication and API endpoints for the tracking application
 */

// Import required modules
const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs').promises;
const cors = require('cors');

// Configuration
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'king-of-the-bay-secret-key';
const DATA_DIR = path.join(__dirname, 'data');

// Create Express app
const app = express();
const server = http.createServer(app);

// Create WebSocket server
const wss = new WebSocket.Server({ server });

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(__dirname));

// In-memory data storage (in a real app, this would be a database)
let participants = [];
let races = [];
let notifications = [];
let sosAlerts = [];

// Load data from files
async function loadData() {
    try {
        // Create data directory if it doesn't exist
        try {
            await fs.mkdir(DATA_DIR, { recursive: true });
        } catch (err) {
            console.error('Error creating data directory:', err);
        }
        
        // Load participants
        try {
            const participantsData = await fs.readFile(path.join(DATA_DIR, 'participants.json'), 'utf8');
            participants = JSON.parse(participantsData);
        } catch (err) {
            console.log('No participants data found, starting with empty array');
            participants = [];
        }
        
        // Load races
        try {
            const racesData = await fs.readFile(path.join(DATA_DIR, 'races.json'), 'utf8');
            races = JSON.parse(racesData);
        } catch (err) {
            console.log('No races data found, starting with empty array');
            races = [];
        }
        
        // Load notifications
        try {
            const notificationsData = await fs.readFile(path.join(DATA_DIR, 'notifications.json'), 'utf8');
            notifications = JSON.parse(notificationsData);
        } catch (err) {
            console.log('No notifications data found, starting with empty array');
            notifications = [];
        }
        
        // Load SOS alerts
        try {
            const sosAlertsData = await fs.readFile(path.join(DATA_DIR, 'sos_alerts.json'), 'utf8');
            sosAlerts = JSON.parse(sosAlertsData);
        } catch (err) {
            console.log('No SOS alerts data found, starting with empty array');
            sosAlerts = [];
        }
        
        console.log('Data loaded successfully');
    } catch (err) {
        console.error('Error loading data:', err);
    }
}

// Save data to files
async function saveData() {
    try {
        // Create data directory if it doesn't exist
        try {
            await fs.mkdir(DATA_DIR, { recursive: true });
        } catch (err) {
            console.error('Error creating data directory:', err);
        }
        
        // Save participants
        await fs.writeFile(path.join(DATA_DIR, 'participants.json'), JSON.stringify(participants, null, 2));
        
        // Save races
        await fs.writeFile(path.join(DATA_DIR, 'races.json'), JSON.stringify(races, null, 2));
        
        // Save notifications
        await fs.writeFile(path.join(DATA_DIR, 'notifications.json'), JSON.stringify(notifications, null, 2));
        
        // Save SOS alerts
        await fs.writeFile(path.join(DATA_DIR, 'sos_alerts.json'), JSON.stringify(sosAlerts, null, 2));
        
        console.log('Data saved successfully');
    } catch (err) {
        console.error('Error saving data:', err);
    }
}

// Initialize with some demo data if empty
async function initializeDemoData() {
    // Check if we have any participants
    if (participants.length === 0) {
        console.log('Initializing demo data...');
        
        // Create organizer account
        participants.push({
            id: uuidv4(),
            username: 'admin',
            password: 'admin123', // In a real app, this would be hashed
            name: 'Administrator',
            role: 'organizer',
            createdAt: new Date().toISOString()
        });
        
        // Create some demo participants
        const demoParticipants = [
            {
                username: 'user1',
                password: 'password',
                name: 'Jan Kowalski',
                sailNumber: 'POL-123',
                trackingColor: '#1a73e8'
            },
            {
                username: 'user2',
                password: 'password',
                name: 'Anna Nowak',
                sailNumber: 'POL-456',
                trackingColor: '#4caf50'
            },
            {
                username: 'user3',
                password: 'password',
                name: 'Piotr Wiśniewski',
                sailNumber: 'POL-789',
                trackingColor: '#f44336'
            }
        ];
        
        demoParticipants.forEach(participant => {
            participants.push({
                id: uuidv4(),
                username: participant.username,
                password: participant.password, // In a real app, this would be hashed
                name: participant.name,
                sailNumber: participant.sailNumber,
                trackingColor: participant.trackingColor,
                role: 'participant',
                isActive: false,
                position: null,
                speed: 0,
                distance: 0,
                lastUpdate: null,
                createdAt: new Date().toISOString()
            });
        });
        
        // Save data
        await saveData();
        
        console.log('Demo data initialized');
    }
}

// WebSocket connection handling
wss.on('connection', (ws) => {
    console.log('New WebSocket connection');
    
    // Set up connection
    ws.isAlive = true;
    ws.isAuthenticated = false;
    ws.userId = null;
    
    // Send connection established message
    ws.send(JSON.stringify({
        type: 'connection_established',
        data: {
            message: 'Connected to King Of theBay tracking server'
        }
    }));
    
    // Handle messages
    ws.on('message', (message) => {
        try {
            const data = JSON.parse(message);
            
            // Handle message based on type
            switch (data.type) {
                case 'auth':
                    handleAuthentication(ws, data.token);
                    break;
                
                case 'position_update':
                    if (ws.isAuthenticated) {
                        handlePositionUpdate(ws, data);
                    } else {
                        sendError(ws, 'Not authenticated');
                    }
                    break;
                
                case 'sos':
                    if (ws.isAuthenticated) {
                        handleSOSAlert(ws, data);
                    } else {
                        sendError(ws, 'Not authenticated');
                    }
                    break;
                
                case 'ping':
                    // Respond with pong
                    ws.send(JSON.stringify({
                        type: 'pong',
                        timestamp: Date.now()
                    }));
                    break;
                
                default:
                    console.log('Unknown message type:', data.type);
            }
        } catch (error) {
            console.error('Error handling message:', error);
            sendError(ws, 'Invalid message format');
        }
    });
    
    // Handle connection close
    ws.on('close', () => {
        console.log('WebSocket connection closed');
        
        // Update participant status if authenticated
        if (ws.isAuthenticated && ws.userId) {
            const participant = participants.find(p => p.id === ws.userId);
            if (participant) {
                participant.isActive = false;
                saveData();
            }
        }
    });
    
    // Handle errors
    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
    
    // Handle pings to keep connection alive
    ws.on('pong', () => {
        ws.isAlive = true;
    });
});

// Ping all clients periodically to keep connections alive
const pingInterval = setInterval(() => {
    wss.clients.forEach((ws) => {
        if (ws.isAlive === false) {
            return ws.terminate();
        }
        
        ws.isAlive = false;
        ws.ping();
    });
}, 30000);

// Clean up interval on server close
wss.on('close', () => {
    clearInterval(pingInterval);
});

// Handle authentication
function handleAuthentication(ws, token) {
    try {
        // Verify token
        const decoded = jwt.verify(token, JWT_SECRET);
        
        // Find participant
        const participant = participants.find(p => p.id === decoded.id);
        
        if (!participant) {
            sendAuthFailure(ws, 'User not found');
            return;
        }
        
        // Set authenticated flag
        ws.isAuthenticated = true;
        ws.userId = participant.id;
        
        // Update participant status
        participant.isActive = true;
        saveData();
        
        // Send success response
        ws.send(JSON.stringify({
            type: 'auth_success',
            data: {
                id: participant.id,
                name: participant.name,
                role: participant.role,
                sailNumber: participant.sailNumber
            }
        }));
        
        console.log(`User authenticated: ${participant.name} (${participant.role})`);
    } catch (error) {
        console.error('Authentication error:', error);
        sendAuthFailure(ws, 'Invalid token');
    }
}

// Handle position update
function handlePositionUpdate(ws, data) {
    // Find participant
    const participant = participants.find(p => p.id === ws.userId);
    
    if (!participant) {
        sendError(ws, 'Participant not found');
        return;
    }
    
    // Update participant position
    participant.position = data.position;
    participant.speed = data.speed || 0;
    participant.distance = data.distance || 0;
    participant.lastUpdate = new Date().toISOString();
    
    // Save data
    saveData();
    
    // Broadcast position update to organizers
    broadcastToOrganizers({
        type: 'participant_position',
        data: {
            participantId: participant.id,
            position: participant.position,
            speed: participant.speed,
            distance: participant.distance,
            timestamp: participant.lastUpdate
        }
    });
}

// Handle SOS alert
function handleSOSAlert(ws, data) {
    // Find participant
    const participant = participants.find(p => p.id === ws.userId);
    
    if (!participant) {
        sendError(ws, 'Participant not found');
        return;
    }
    
    // Create SOS alert
    const sosAlert = {
        id: uuidv4(),
        participantId: participant.id,
        position: data.position,
        time: new Date().toISOString(),
        resolved: false
    };
    
    // Add to SOS alerts
    sosAlerts.push(sosAlert);
    
    // Save data
    saveData();
    
    // Broadcast SOS alert to organizers
    broadcastToOrganizers({
        type: 'sos_alert',
        data: sosAlert
    });
    
    // Send confirmation to participant
    ws.send(JSON.stringify({
        type: 'sos_confirmation',
        data: {
            message: 'SOS alert sent successfully',
            alertId: sosAlert.id
        }
    }));
    
    console.log(`SOS alert from ${participant.name} (${participant.sailNumber})`);
}

// Send authentication failure
function sendAuthFailure(ws, message) {
    ws.send(JSON.stringify({
        type: 'auth_failure',
        data: {
            message
        }
    }));
}

// Send error message
function sendError(ws, message) {
    ws.send(JSON.stringify({
        type: 'error',
        data: {
            message
        }
    }));
}

// Broadcast message to all organizers
function broadcastToOrganizers(message) {
    wss.clients.forEach((client) => {
        if (client.isAuthenticated && client.userId) {
            const participant = participants.find(p => p.id === client.userId);
            
            if (participant && participant.role === 'organizer') {
                client.send(JSON.stringify(message));
            }
        }
    });
}

// Broadcast message to all participants
function broadcastToParticipants(message) {
    wss.clients.forEach((client) => {
        if (client.isAuthenticated && client.userId) {
            const participant = participants.find(p => p.id === client.userId);
            
            if (participant && participant.role === 'participant') {
                client.send(JSON.stringify(message));
            }
        }
    });
}

// Broadcast message to specific participant
function broadcastToParticipant(participantId, message) {
    wss.clients.forEach((client) => {
        if (client.isAuthenticated && client.userId === participantId) {
            client.send(JSON.stringify(message));
        }
    });
}

// Broadcast message to all active participants
function broadcastToActiveParticipants(message) {
    const activeParticipantIds = participants
        .filter(p => p.isActive && p.role === 'participant')
        .map(p => p.id);
    
    wss.clients.forEach((client) => {
        if (client.isAuthenticated && client.userId && activeParticipantIds.includes(client.userId)) {
            client.send(JSON.stringify(message));
        }
    });
}

// API Routes

// Authentication routes
app.post('/api/auth/register', async (req, res) => {
    try {
        const { username, password, name, sailNumber } = req.body;
        
        // Validate input
        if (!username || !password || !name || !sailNumber) {
            return res.status(400).json({ error: 'All fields are required' });
        }
        
        // Check if username already exists
        if (participants.some(p => p.username === username)) {
            return res.status(400).json({ error: 'Username already exists' });
        }
        
        // Create new participant
        const newParticipant = {
            id: uuidv4(),
            username,
            password, // In a real app, this would be hashed
            name,
            sailNumber,
            trackingColor: '#1a73e8', // Default color
            role: 'participant',
            isActive: false,
            position: null,
            speed: 0,
            distance: 0,
            lastUpdate: null,
            createdAt: new Date().toISOString()
        };
        
        // Add to participants
        participants.push(newParticipant);
        
        // Save data
        await saveData();
        
        // Return success
        res.status(201).json({
            message: 'Registration successful',
            id: newParticipant.id
        });
    } catch (error) {
        console.error('Registration error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.post('/api/auth/login', (req, res) => {
    try {
        const { username, password } = req.body;
        
        // Validate input
        if (!username || !password) {
            return res.status(400).json({ error: 'Username and password are required' });
        }
        
        // Find participant
        const participant = participants.find(p => p.username === username && p.password === password);
        
        if (!participant) {
            return res.status(401).json({ error: 'Invalid username or password' });
        }
        
        // Generate token
        const token = jwt.sign(
            { id: participant.id, role: participant.role },
            JWT_SECRET,
            { expiresIn: '24h' }
        );
        
        // Return token and user info
        res.json({
            token,
            id: participant.id,
            name: participant.name,
            role: participant.role,
            sailNumber: participant.sailNumber
        });
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Middleware to verify JWT token
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    
    if (!token) {
        return res.status(401).json({ error: 'Authentication token required' });
    }
    
    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ error: 'Invalid or expired token' });
        }
        
        req.user = user;
        next();
    });
}

// Middleware to check if user is organizer
function isOrganizer(req, res, next) {
    if (req.user.role !== 'organizer') {
        return res.status(403).json({ error: 'Access denied' });
    }
    
    next();
}

// Participant routes
app.get('/api/participants', authenticateToken, (req, res) => {
    // Return participants without sensitive information
    const safeParticipants = participants
        .filter(p => p.role === 'participant')
        .map(p => ({
            id: p.id,
            name: p.name,
            sailNumber: p.sailNumber,
            trackingColor: p.trackingColor,
            isActive: p.isActive,
            position: p.position,
            speed: p.speed,
            distance: p.distance,
            lastUpdate: p.lastUpdate
        }));
    
    res.json(safeParticipants);
});

app.put('/api/participants', authenticateToken, async (req, res) => {
    try {
        const { name, sailNumber, trackingColor } = req.body;
        
        // Find participant
        const participant = participants.find(p => p.id === req.user.id);
        
        if (!participant) {
            return res.status(404).json({ error: 'Participant not found' });
        }
        
        // Update participant
        if (name) participant.name = name;
        if (sailNumber) participant.sailNumber = sailNumber;
        if (trackingColor) participant.trackingColor = trackingColor;
        
        // Save data
        await saveData();
        
        // Return updated participant
        res.json({
            id: participant.id,
            name: participant.name,
            sailNumber: participant.sailNumber,
            trackingColor: participant.trackingColor
        });
    } catch (error) {
        console.error('Update participant error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Race routes
app.get('/api/races', authenticateToken, (req, res) => {
    // Return races
    res.json(races);
});

app.get('/api/races/active', authenticateToken, (req, res) => {
    // Find active race
    const activeRace = races.find(r => r.status === 'active' || r.status === 'paused');
    
    if (!activeRace) {
        return res.status(404).json({ error: 'No active race found' });
    }
    
    // Return active race
    res.json(activeRace);
});

app.post('/api/races', authenticateToken, isOrganizer, async (req, res) => {
    try {
        const { name, status, startTime } = req.body;
        
        // Validate input
        if (!name || !status) {
            return res.status(400).json({ error: 'Name and status are required' });
        }
        
        // Create new race
        const newRace = {
            id: uuidv4(),
            name,
            status,
            startTime: startTime || new Date().toISOString(),
            endTime: null,
            createdBy: req.user.id,
            createdAt: new Date().toISOString(),
            results: []
        };
        
        // Add to races
        races.push(newRace);
        
        // Save data
        await saveData();
        
        // Broadcast race update
        broadcastToParticipants({
            type: 'race_update',
            data: {
                id: newRace.id,
                name: newRace.name,
                status: newRace.status,
                startTime: newRace.startTime
            }
        });
        
        // Return new race
        res.status(201).json(newRace);
    } catch (error) {
        console.error('Create race error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.post('/api/races/:id/pause', authenticateToken, isOrganizer, async (req, res) => {
    try {
        const raceId = req.params.id;
        
        // Find race
        const race = races.find(r => r.id === raceId);
        
        if (!race) {
            return res.status(404).json({ error: 'Race not found' });
        }
        
        // Update race status
        race.status = 'paused';
        
        // Save data
        await saveData();
        
        // Broadcast race update
        broadcastToParticipants({
            type: 'race_update',
            data: {
                id: race.id,
                name: race.name,
                status: race.status
            }
        });
        
        // Return updated race
        res.json(race);
    } catch (error) {
        console.error('Pause race error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.post('/api/races/:id/resume', authenticateToken, isOrganizer, async (req, res) => {
    try {
        const raceId = req.params.id;
        
        // Find race
        const race = races.find(r => r.id === raceId);
        
        if (!race) {
            return res.status(404).json({ error: 'Race not found' });
        }
        
        // Update race status
        race.status = 'active';
        
        // Save data
        await saveData();
        
        // Broadcast race update
        broadcastToParticipants({
            type: 'race_update',
            data: {
                id: race.id,
                name: race.name,
                status: race.status
            }
        });
        
        // Return updated race
        res.json(race);
    } catch (error) {
        console.error('Resume race error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.post('/api/races/:id/end', authenticateToken, isOrganizer, async (req, res) => {
    try {
        const raceId = req.params.id;
        
        // Find race
        const race = races.find(r => r.id === raceId);
        
        if (!race) {
            return res.status(404).json({ error: 'Race not found' });
        }
        
        // Update race status
        race.status = 'finished';
        race.endTime = new Date().toISOString();
        
        // Calculate results
        race.results = participants
            .filter(p => p.role === 'participant' && p.distance > 0)
            .map(p => ({
                userId: p.id,
                name: p.name,
                sailNumber: p.sailNumber,
                distance: p.distance,
                time: Math.floor((new Date(p.lastUpdate) - new Date(race.startTime)) / 1000) // Time in seconds
            }))
            .sort((a, b) => b.distance - a.distance); // Sort by distance
        
        // Save data
        await saveData();
        
        // Broadcast race update
        broadcastToParticipants({
            type: 'race_update',
            data: {
                id: race.id,
                name: race.name,
                status: race.status,
                endTime: race.endTime,
                results: race.results
            }
        });
        
        // Return updated race
        res.json(race);
    } catch (error) {
        console.error('End race error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Notification routes
app.post('/api/notifications', authenticateToken, isOrganizer, async (req, res) => {
    try {
        const { title, message, type, recipient } = req.body;
        
        // Validate input
        if (!title || !message) {
            return res.status(400).json({ error: 'Title and message are required' });
        }
        
        // Create notification
        const notification = {
            id: uuidv4(),
            title,
            message,
            type: type || 'info',
            recipient,
            createdBy: req.user.id,
            createdAt: new Date().toISOString()
        };
        
        // Add to notifications
        notifications.push(notification);
        
        // Save data
        await saveData();
        
        // Broadcast notification
        if (recipient === 'all') {
            // Send to all participants
            broadcastToParticipants({
                type: 'notification',
                data: notification
            });
        } else if (recipient === 'active') {
            // Send to active participants
            broadcastToActiveParticipants({
                type: 'notification',
                data: notification
            });
        } else {
            // Send to specific participant
            broadcastToParticipant(recipient, {
                type: 'notification',
                data: notification
            });
        }
        
        // Return notification
        res.status(201).json(notification);
    } catch (error) {
        console.error('Create notification error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// SOS routes
app.post('/api/sos/:id/resolve', authenticateToken, isOrganizer, async (req, res) => {
    try {
        const alertId = req.params.id;
        
        // Find alert
        const alert = sosAlerts.find(a => a.id === alertId);
        
        if (!alert) {
            return res.status(404).json({ error: 'SOS alert not found' });
        }
        
        // Update alert
        alert.resolved = true;
        alert.resolvedBy = req.user.id;
        alert.resolvedAt = new Date().toISOString();
        
        // Save data
        await saveData();
        
        // Broadcast update
        broadcastToOrganizers({
            type: 'sos_update',
            data: alert
        });
        
        // Return updated alert
        res.json(alert);
    } catch (error) {
        console.error('Resolve SOS alert error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Serve static files
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.get('/organizer', (req, res) => {
    res.sendFile(path.join(__dirname, 'organizer-view.html'));
});

// Handle 404
app.use((req, res) => {
    res.status(404).sendFile(path.join(__dirname, '404.html'));
});

// Start server
async function startServer() {
    // Load data
    await loadData();
    
    // Initialize demo data
    await initializeDemoData();
    
    // Start server
    server.listen(PORT, () => {
        console.log(`Server running on port ${PORT}`);
    });
}

// Start server
startServer();
