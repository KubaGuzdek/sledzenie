# Render.com WebSocket Configuration Guide

## Background

Render.com has specific requirements for WebSocket implementations:

1. Render.com does not support custom ports in Web Services
2. Render.com only allows port 10000 for WebSockets, but not in Web Service type
3. Render requires WebSockets to be configured as Background Workers, where Render listens and forwards WebSockets to your application

## Configuration Changes

We've made the following changes to adapt our application to Render.com's WebSocket requirements:

### 1. Updated render.yaml

We've split our service into two parts:
- A static web service for serving the frontend files
- A background worker for handling WebSocket connections

```yaml
# Render.yaml configuration file
services:
  # Web service for the frontend static files
  - type: web
    name: king-of-the-bay
    env: static
    buildCommand: echo "Static site ready"
    staticPublishPath: ./
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
    healthCheckPath: /
  
  # Background Worker for WebSocket server
  - type: worker
    name: king-of-the-bay-websocket
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python websocket_server.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
```

### 2. Updated Client-Side WebSocket Connection

In `js/tracking-communication.js`, we've updated the WebSocket URL for Render.com:

```javascript
// Before:
url = "wss://sledzenie.onrender.com:10000/ws";

// After:
url = "wss://sledzenie.onrender.com/ws";
```

This change removes the port specification, as Render.com handles the WebSocket routing internally when using a Background Worker.

### 3. Updated Test WebSocket Client

In `test_render_websocket.py`, we've updated the WebSocket URL to match the new format:

```javascript
// Before:
const url = "wss://sledzenie.onrender.com:10000/ws";

// After:
const url = "wss://sledzenie.onrender.com/ws";
```

## How It Works

1. When deployed to Render.com, the static web service serves your frontend files
2. The background worker runs your WebSocket server on port 10000
3. Render.com handles the routing of WebSocket connections to your background worker
4. Clients connect to `wss://sledzenie.onrender.com/ws` (without specifying a port)
5. Render.com forwards these connections to your background worker

## Testing Locally

You can still test your WebSocket server locally using the `test_render_websocket.py` script, which will:
1. Start a local HTTP server on port 8000
2. Start your WebSocket server on port 10000
3. Open a test page in your browser

When testing locally, the WebSocket server will still use port 10000, but when deployed to Render.com, the routing will be handled by Render's infrastructure.

## Important Notes

- The WebSocket server code in `websocket_server.py` already accepts connections on the "/ws" path, which is required for Render.com
- The server listens on port 10000, which is the port Render.com expects for WebSocket background workers
- When deployed to Render.com, clients should connect to the WebSocket without specifying a port
