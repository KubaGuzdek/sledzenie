#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test client for the WebSocket server
This script connects to the WebSocket server and sends test messages
"""

import asyncio
import websockets
import json
import logging
import time
import random

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

async def test_client():
    """Test client that connects to the WebSocket server"""
    
    # Connect to server
    uri = "ws://localhost:8765"
    logging.info(f"Connecting to {uri}...")
    
    async with websockets.connect(uri) as websocket:
        logging.info("Connected to server")
        
        # Wait for connection established message
        response = await websocket.recv()
        logging.info(f"Received: {response}")
        
        # Send auth message
        auth_message = {
            "type": "auth",
            "token": "test_token"
        }
        logging.info(f"Sending auth message: {auth_message}")
        await websocket.send(json.dumps(auth_message))
        
        # Wait for auth response
        response = await websocket.recv()
        logging.info(f"Received: {response}")
        
        # Send position updates
        for i in range(5):
            # Generate random position
            lat = 54.0 + random.random() * 0.1
            lng = 18.5 + random.random() * 0.1
            
            position_message = {
                "type": "position_update",
                "position": {
                    "lat": lat,
                    "lng": lng
                },
                "speed": random.random() * 10,
                "distance": i * 100
            }
            
            logging.info(f"Sending position update: {position_message}")
            await websocket.send(json.dumps(position_message))
            
            # Wait for a moment
            await asyncio.sleep(1)
        
        # Send SOS message
        sos_message = {
            "type": "sos",
            "position": {
                "lat": 54.05,
                "lng": 18.55
            }
        }
        
        logging.info(f"Sending SOS message: {sos_message}")
        await websocket.send(json.dumps(sos_message))
        
        # Wait for SOS response
        response = await websocket.recv()
        logging.info(f"Received: {response}")
        
        # Send ping message
        ping_message = {
            "type": "ping",
            "timestamp": time.time() * 1000
        }
        
        logging.info(f"Sending ping message: {ping_message}")
        await websocket.send(json.dumps(ping_message))
        
        # Wait for pong response
        response = await websocket.recv()
        logging.info(f"Received: {response}")
        
        logging.info("Test completed successfully")

if __name__ == "__main__":
    try:
        asyncio.run(test_client())
    except Exception as e:
        logging.error(f"Error: {e}")
