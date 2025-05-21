"""
WSGI configuration for Render.com
This file is used by Render.com to serve both the WebSocket server and the static files
"""

import os
import sys
import mimetypes
import threading
import asyncio
import websockets
import logging
import json
from aiohttp import web

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add the current directory to the path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Import the WebSocket server
from websocket_server import TrackingServer

# Create a wrapper for aiohttp WebSocketResponse to make it compatible with TrackingServer
class WebSocketWrapper:
    def __init__(self, ws):
        self.ws = ws
    
    async def send(self, message):
        await self.ws.send_str(message)

# Configure mimetypes
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('image/png', '.png')
mimetypes.add_type('image/jpeg', '.jpg')
mimetypes.add_type('image/jpeg', '.jpeg')

# Create a WSGI application that serves static files
def create_wsgi_app():
    """Create a WSGI application that serves static files"""
    def application(environ, start_response):
        """
        WSGI application that serves static files
        """
        # Get the request path
        path_info = environ.get('PATH_INFO', '/')
        
        # Normalize path
        if path_info == '/':
            path_info = '/index.html'
        
        # Get the file path
        file_path = os.path.join(path, path_info.lstrip('/'))
        
        # Check if the file exists
        if os.path.isfile(file_path):
            # Get the file extension
            _, ext = os.path.splitext(file_path)
            
            # Get the content type
            content_type = mimetypes.types_map.get(ext.lower(), 'text/plain')
            
            # Read the file
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Return the file
            status = '200 OK'
            headers = [
                ('Content-type', content_type),
                ('Content-Length', str(len(file_content)))
            ]
            start_response(status, headers)
            
            return [file_content]
        else:
            # Return 404 if the file doesn't exist
            status = '404 Not Found'
            headers = [('Content-type', 'text/html')]
            start_response(status, headers)
            
            # Try to read the 404.html file
            try:
                with open(os.path.join(path, '404.html'), 'rb') as f:
                    return [f.read()]
            except:
                return [b'<html><body><h1>404 Not Found</h1></body></html>']
    
    return application

# Create the WSGI application
application = create_wsgi_app()

# Function to run the combined HTTP and WebSocket server
async def run_server():
    """Run the combined HTTP and WebSocket server"""
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 10000))
    
    # Create an aiohttp web application
    app = web.Application()
    
    # Add routes for static files
    app.router.add_static('/', path)
    
    # Create WebSocket server
    server = TrackingServer()
    logger.info("WebSocket server created")
    
    # Add WebSocket route
    async def websocket_handler(request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        logger.info(f"WebSocket connection established from {request.remote}")
        
        # Wrap the WebSocket connection to make it compatible with TrackingServer
        wrapped_ws = WebSocketWrapper(ws)
        
        # Register the wrapped WebSocket connection
        connection_id = await server.register(wrapped_ws)
        
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    try:
                        # Parse message
                        data = json.loads(msg.data)
                        message_type = data.get("type")
                        
                        # Handle message based on type
                        if message_type == "auth":
                            await server.handle_auth(connection_id, data)
                        elif message_type == "position_update":
                            await server.handle_position_update(connection_id, data)
                        elif message_type == "sos":
                            await server.handle_sos(connection_id, data)
                        elif message_type == "ping":
                            await server.handle_ping(connection_id, data)
                        else:
                            logger.warning(f"Unknown message type: {message_type}")
                    
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON: {msg.data}")
                    except Exception as e:
                        logger.error(f"Error handling message: {e}")
                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f"WebSocket connection closed with exception {ws.exception()}")
        
        finally:
            await server.unregister(connection_id)
        
        return ws
    
    # Add WebSocket route
    app.router.add_get('/ws', websocket_handler)
    
    # Start the server
    logger.info(f"Starting combined HTTP and WebSocket server on port {port}")
    
    # Create the runner
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Create the site
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    # Start the site
    await site.start()
    
    # Keep the server running
    while True:
        await asyncio.sleep(3600)  # Sleep for an hour

# Main function
if __name__ == "__main__":
    logger.info("King Of theBay application started")
    
    # Run the combined server
    asyncio.run(run_server())
else:
    # Create an event loop for the combined server
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Start the combined server in a background task
    async def start_server():
        await run_server()
    
    # Create a background task
    task = loop.create_task(start_server())
    
    logger.info("King Of theBay application started (module mode)")
