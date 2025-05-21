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
from concurrent.futures import ThreadPoolExecutor

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

# Function to run the HTTP server
def run_http_server():
    """Run the HTTP server"""
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8765))
    
    # Create an aiohttp web application
    app = web.Application()
    
    # Add routes for static files
    app.router.add_static('/', path)
    
    # Start the server
    logger.info(f"Starting HTTP server on port {port}")
    web.run_app(app, port=port)

# Function to run the WebSocket server
async def run_websocket_server():
    """Run the WebSocket server"""
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8765))
    
    # Create WebSocket server
    server = TrackingServer()
    logger.info("WebSocket server created")
    
    # Start server
    async with websockets.serve(
        server.handle_client,
        "0.0.0.0",  # Listen on all interfaces
        port,       # Port number
        path="/ws"  # Use a specific path for WebSocket connections
    ):
        logger.info(f"WebSocket server started on port {port} with path /ws")
        await asyncio.Future()  # Run forever

# Main function
if __name__ == "__main__":
    logger.info("King Of theBay application started")
    
    # Run the HTTP server in a separate thread
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(run_http_server)
        
        # Run the WebSocket server in the main thread
        asyncio.run(run_websocket_server())
else:
    # For WSGI mode, we need to start the WebSocket server in a background thread
    async def start_websocket_server():
        await run_websocket_server()
    
    # Create a new event loop for the WebSocket server
    websocket_loop = asyncio.new_event_loop()
    
    # Run the WebSocket server in a separate thread
    def run_websocket_server_thread():
        asyncio.set_event_loop(websocket_loop)
        websocket_loop.run_until_complete(start_websocket_server())
    
    websocket_thread = threading.Thread(target=run_websocket_server_thread)
    websocket_thread.daemon = True
    websocket_thread.start()
    
    logger.info("King Of theBay application started (WSGI mode)")
    logger.info("WebSocket server running in background thread")
