"""
WSGI configuration for Render.com
This file is used by Render.com to serve both the WebSocket server and the static files
"""

import os
import sys
import mimetypes
import asyncio
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

# WebSocket connection handler
async def websocket_handler(request):
    """Handle WebSocket connections"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    logger.info(f"WebSocket connection established from {request.remote}")
    
    # Create TrackingServer instance
    server = TrackingServer()
    
    # Register the connection
    connection_id = None
    
    try:
        # Create a custom send method for the WebSocket
        async def custom_send(message):
            await ws.send_str(message)
        
        # Create a custom WebSocket object that matches what TrackingServer expects
        class CustomWebSocket:
            async def send(self, message):
                await custom_send(message)
        
        custom_ws = CustomWebSocket()
        
        # Register the connection
        connection_id = await server.register(custom_ws)
        
        # Process messages
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
    
    except Exception as e:
        logger.error(f"Error in websocket_handler: {e}")
    
    finally:
        # Unregister the connection
        if connection_id:
            await server.unregister(connection_id)
        
        logger.info(f"WebSocket connection closed from {request.remote}")
    
    return ws

# Create and run the aiohttp application
async def create_app():
    """Create and configure the aiohttp application"""
    app = web.Application()
    
    # Add routes
    app.router.add_get('/ws', websocket_handler)
    app.router.add_static('/', path)
    
    return app

# Main function
if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8765))
    
    logger.info(f"Starting server on port {port}")
    logger.info("King Of theBay application started")
    
    # Run the application
    web.run_app(create_app(), port=port)
else:
    # For WSGI mode, we need to create the application
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app = loop.run_until_complete(create_app())
    
    logger.info("King Of theBay application started (WSGI mode)")
