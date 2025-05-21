#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
King Of theBay WebSocket Server for PythonAnywhere
This script handles WebSocket connections for the tracking application
"""

import asyncio
import json
import logging
import websockets
import ssl
import pathlib
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

# In-memory data storage
participants = {}
active_connections = {}
organizer_connections = set()
participant_connections = {}

class TrackingServer:
    def __init__(self):
        self.participants = {}
        self.active_connections = {}
        self.organizer_connections = set()
        self.participant_connections = {}
    
    async def register(self, websocket):
        """Register a new client connection"""
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = {
            "websocket": websocket,
            "is_authenticated": False,
            "user_id": None,
            "role": None,
            "last_activity": datetime.now().isoformat()
        }
        logging.info(f"New connection registered: {connection_id}")
        
        # Send connection established message
        await websocket.send(json.dumps({
            "type": "connection_established",
            "data": {
                "message": "Connected to King Of theBay tracking server (PythonAnywhere)"
            }
        }))
        
        return connection_id
    
    async def unregister(self, connection_id):
        """Unregister a client connection"""
        if connection_id in self.active_connections:
            connection = self.active_connections[connection_id]
            
            # Remove from role-specific collections
            if connection["role"] == "organizer" and connection_id in self.organizer_connections:
                self.organizer_connections.remove(connection_id)
            
            if connection["role"] == "participant" and connection["user_id"] in self.participant_connections:
                if connection_id in self.participant_connections[connection["user_id"]]:
                    self.participant_connections[connection["user_id"]].remove(connection_id)
                
                # Clean up empty participant connections
                if not self.participant_connections[connection["user_id"]]:
                    del self.participant_connections[connection["user_id"]]
            
            # Remove from active connections
            del self.active_connections[connection_id]
            logging.info(f"Connection unregistered: {connection_id}")
    
    async def handle_auth(self, connection_id, data):
        """Handle authentication message"""
        connection = self.active_connections.get(connection_id)
        if not connection:
            return
        
        # In a real implementation, you would verify the token
        # For this example, we'll just simulate successful authentication
        
        # Simulate user data
        user_id = str(uuid.uuid4())
        name = f"User {user_id[:8]}"
        role = "participant"  # or "organizer"
        
        # Update connection
        connection["is_authenticated"] = True
        connection["user_id"] = user_id
        connection["role"] = role
        
        # Add to role-specific collections
        if role == "organizer":
            self.organizer_connections.add(connection_id)
        
        if role == "participant":
            if user_id not in self.participant_connections:
                self.participant_connections[user_id] = set()
            self.participant_connections[user_id].add(connection_id)
        
        # Send success response
        await connection["websocket"].send(json.dumps({
            "type": "auth_success",
            "data": {
                "id": user_id,
                "name": name,
                "role": role,
                "sailNumber": f"POL-{user_id[:3]}"
            }
        }))
        
        logging.info(f"Authentication successful for connection {connection_id}: {name} ({role})")
    
    async def handle_position_update(self, connection_id, data):
        """Handle position update message"""
        connection = self.active_connections.get(connection_id)
        if not connection or not connection["is_authenticated"]:
            return
        
        # Extract data
        position = data.get("position")
        speed = data.get("speed", 0)
        distance = data.get("distance", 0)
        timestamp = datetime.now().isoformat()
        
        # Broadcast to organizers
        await self.broadcast_to_organizers({
            "type": "participant_position",
            "data": {
                "participantId": connection["user_id"],
                "position": position,
                "speed": speed,
                "distance": distance,
                "timestamp": timestamp
            }
        })
        
        logging.info(f"Position update from {connection['user_id']}: {position}")
    
    async def handle_sos(self, connection_id, data):
        """Handle SOS alert message"""
        connection = self.active_connections.get(connection_id)
        if not connection or not connection["is_authenticated"]:
            return
        
        # Extract data
        position = data.get("position")
        alert_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Create SOS alert
        sos_alert = {
            "id": alert_id,
            "participantId": connection["user_id"],
            "position": position,
            "time": timestamp,
            "resolved": False
        }
        
        # Broadcast to organizers
        await self.broadcast_to_organizers({
            "type": "sos_alert",
            "data": sos_alert
        })
        
        # Send confirmation to participant
        await connection["websocket"].send(json.dumps({
            "type": "sos_confirmation",
            "data": {
                "message": "SOS alert sent successfully",
                "alertId": alert_id
            }
        }))
        
        logging.info(f"SOS alert from {connection['user_id']}: {position}")
    
    async def handle_ping(self, connection_id, data):
        """Handle ping message"""
        connection = self.active_connections.get(connection_id)
        if not connection:
            return
        
        # Update last activity
        connection["last_activity"] = datetime.now().isoformat()
        
        # Send pong
        await connection["websocket"].send(json.dumps({
            "type": "pong",
            "timestamp": data.get("timestamp", datetime.now().timestamp() * 1000)
        }))
    
    async def broadcast_to_organizers(self, message):
        """Broadcast message to all organizers"""
        for connection_id in self.organizer_connections:
            connection = self.active_connections.get(connection_id)
            if connection and connection["is_authenticated"]:
                try:
                    await connection["websocket"].send(json.dumps(message))
                except Exception as e:
                    logging.error(f"Error broadcasting to organizer {connection_id}: {e}")
    
    async def broadcast_to_participants(self, message):
        """Broadcast message to all participants"""
        for user_id, connections in self.participant_connections.items():
            for connection_id in connections:
                connection = self.active_connections.get(connection_id)
                if connection and connection["is_authenticated"]:
                    try:
                        await connection["websocket"].send(json.dumps(message))
                    except Exception as e:
                        logging.error(f"Error broadcasting to participant {connection_id}: {e}")
    
    async def broadcast_to_participant(self, user_id, message):
        """Broadcast message to a specific participant"""
        if user_id not in self.participant_connections:
            return
        
        for connection_id in self.participant_connections[user_id]:
            connection = self.active_connections.get(connection_id)
            if connection and connection["is_authenticated"]:
                try:
                    await connection["websocket"].send(json.dumps(message))
                except Exception as e:
                    logging.error(f"Error broadcasting to participant {connection_id}: {e}")
    
    async def handle_client(self, websocket, path):
        """Handle a client connection"""
        connection_id = await self.register(websocket)
        
        try:
            async for message in websocket:
                try:
                    # Parse message
                    data = json.loads(message)
                    message_type = data.get("type")
                    
                    # Handle message based on type
                    if message_type == "auth":
                        await self.handle_auth(connection_id, data)
                    elif message_type == "position_update":
                        await self.handle_position_update(connection_id, data)
                    elif message_type == "sos":
                        await self.handle_sos(connection_id, data)
                    elif message_type == "ping":
                        await self.handle_ping(connection_id, data)
                    else:
                        logging.warning(f"Unknown message type: {message_type}")
                
                except json.JSONDecodeError:
                    logging.error(f"Invalid JSON: {message}")
                except Exception as e:
                    logging.error(f"Error handling message: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            logging.info(f"Connection closed: {connection_id}")
        
        finally:
            await self.unregister(connection_id)

async def main():
    # Create server instance
    server = TrackingServer()
    
    # Set up SSL context (if needed)
    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # ssl_context.load_cert_chain(pathlib.Path("cert.pem"), pathlib.Path("key.pem"))
    
    # Start server
    async with websockets.serve(
        server.handle_client,
        "0.0.0.0",  # Listen on all interfaces
        8765,       # Port number
        # ssl=ssl_context  # Uncomment for SSL
    ):
        logging.info("Server started on ws://0.0.0.0:8765 (use /ws path for Render.com)")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped")
