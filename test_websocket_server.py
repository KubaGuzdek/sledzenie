#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for the WebSocket server
This script starts the WebSocket server locally for testing
"""

import asyncio
import websockets
import json
import logging
from websocket_server import TrackingServer

# Configure logging
logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

async def main():
    # Create server instance
    server = TrackingServer()
    
    # Start server
    async with websockets.serve(
        server.handle_client,
        "localhost",  # Listen only on localhost for testing
        8765,         # Port number
    ):
        logging.info("Test server started on ws://localhost:8765")
        logging.info("Press Ctrl+C to stop the server")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped")
