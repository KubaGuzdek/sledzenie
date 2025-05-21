#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Skrypt testowy dla konfiguracji WebSocket na Render.com
Ten skrypt uruchamia lokalnie serwer WebSocket z konfiguracją Render.com
i pozwala przetestować, czy wszystko działa poprawnie przed wdrożeniem.
"""

import os
import sys
import asyncio
import websockets
import logging
import webbrowser
import signal
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Importuj TrackingServer z websocket_server.py
try:
    from websocket_server import TrackingServer
    logger.info("Zaimportowano TrackingServer z websocket_server.py")
except ImportError:
    logger.error("Nie można zaimportować TrackingServer z websocket_server.py")
    logger.error("Upewnij się, że plik websocket_server.py znajduje się w bieżącym katalogu")
    sys.exit(1)

# Klasa serwera HTTP
class RenderHTTPHandler(SimpleHTTPRequestHandler):
    """Prosty serwer HTTP do obsługi plików statycznych"""
    
    def log_message(self, format, *args):
        """Nadpisz metodę logowania, aby używać naszego loggera"""
        logger.info("%s - %s" % (self.address_string(), format % args))
    
    def end_headers(self):
        """Dodaj nagłówki CORS"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        SimpleHTTPRequestHandler.end_headers(self)

# Funkcja uruchamiająca serwer HTTP
def run_http_server(port=8000):
    """Uruchom serwer HTTP na podanym porcie"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, RenderHTTPHandler)
    logger.info(f"Uruchamianie serwera HTTP na porcie {port}")
    httpd.serve_forever()

# Funkcja uruchamiająca serwer WebSocket
async def run_websocket_server(port=10000):
    """Uruchom serwer WebSocket na podanym porcie"""
    server = TrackingServer()
    logger.info(f"Uruchamianie serwera WebSocket na porcie {port}")
    
    async with websockets.serve(server.handle_client, "", port):
        logger.info(f"Serwer WebSocket uruchomiony na porcie {port} (use /ws path for Render.com)")
        await asyncio.Future()  # Uruchom serwer w nieskończoność

# Funkcja główna
async def main():
    """Funkcja główna"""
    logger.info("=== Test konfiguracji WebSocket dla Render.com ===")
    
    # Sprawdź, czy istnieją wymagane pliki
    required_files = [
        "websocket_server.py",
        "index.html",
        "js/tracking-communication.js"
    ]
    
    for file in required_files:
        if not os.path.isfile(file):
            logger.error(f"Brak wymaganego pliku: {file}")
            logger.error("Upewnij się, że uruchamiasz skrypt z głównego katalogu projektu")
            return
    
    # Uruchom serwer HTTP w osobnym wątku
    http_port = 8000
    http_thread = threading.Thread(target=run_http_server, args=(http_port,), daemon=True)
    http_thread.start()
    logger.info(f"Serwer HTTP uruchomiony w tle na porcie {http_port}")
    
    # Uruchom serwer WebSocket
    websocket_port = 10000
    websocket_task = asyncio.create_task(run_websocket_server(websocket_port))
    
    # Otwórz przeglądarkę z testową stroną
    test_url = f"http://localhost:{http_port}/websocket_test.html"
    
    # Sprawdź, czy istnieje plik websocket_test.html
    if os.path.isfile("websocket_test.html"):
        logger.info(f"Otwieranie przeglądarki z testową stroną: {test_url}")
        webbrowser.open(test_url)
    else:
        # Jeśli nie ma pliku testowego, utwórz go
        logger.info("Tworzenie pliku testowego websocket_test.html")
        with open("websocket_test.html", "w") as f:
            f.write("""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test WebSocket dla Render.com</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .connected {
            background-color: #d4edda;
            color: #155724;
        }
        .disconnected {
            background-color: #f8d7da;
            color: #721c24;
        }
        .log {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 10px;
            height: 300px;
            overflow-y: auto;
            font-family: monospace;
        }
        button {
            padding: 8px 16px;
            margin: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>Test WebSocket dla Render.com</h1>
    
    <div id="status" class="status disconnected">
        Status: Rozłączony
    </div>
    
    <div>
        <button id="connectBtn">Połącz</button>
        <button id="disconnectBtn" disabled>Rozłącz</button>
        <button id="pingBtn" disabled>Wyślij Ping</button>
        <button id="authBtn" disabled>Symuluj Autoryzację</button>
        <button id="positionBtn" disabled>Wyślij Pozycję</button>
    </div>
    
    <h2>Logi</h2>
    <div id="log" class="log"></div>
    
    <script>
        // Elementy DOM
        const statusEl = document.getElementById('status');
        const logEl = document.getElementById('log');
        const connectBtn = document.getElementById('connectBtn');
        const disconnectBtn = document.getElementById('disconnectBtn');
        const pingBtn = document.getElementById('pingBtn');
        const authBtn = document.getElementById('authBtn');
        const positionBtn = document.getElementById('positionBtn');
        
        // Zmienne WebSocket
        let socket = null;
        let isConnected = false;
        
        // Funkcja dodająca log
        function log(message, type = 'info') {
            const now = new Date().toLocaleTimeString();
            const logItem = document.createElement('div');
            logItem.innerHTML = `<span style="color: #666;">[${now}]</span> <span class="${type}">${message}</span>`;
            logEl.appendChild(logItem);
            logEl.scrollTop = logEl.scrollHeight;
        }
        
        // Funkcja aktualizująca status
        function updateStatus(connected) {
            isConnected = connected;
            statusEl.className = connected ? 'status connected' : 'status disconnected';
            statusEl.textContent = connected ? 'Status: Połączony' : 'Status: Rozłączony';
            
            connectBtn.disabled = connected;
            disconnectBtn.disabled = !connected;
            pingBtn.disabled = !connected;
            authBtn.disabled = !connected;
            positionBtn.disabled = !connected;
        }
        
        // Funkcja łącząca z serwerem WebSocket
        function connect() {
            try {
                // Utwórz URL WebSocket - dla Render.com używamy standardowego URL bez portu
                const url = "wss://sledzenie.onrender.com/ws";
                
                log(`Łączenie z serwerem WebSocket: ${url}`);
                
                // Utwórz połączenie WebSocket
                socket = new WebSocket(url);
                
                // Obsługa zdarzeń WebSocket
                socket.onopen = () => {
                    log('Połączono z serwerem WebSocket', 'success');
                    updateStatus(true);
                };
                
                socket.onmessage = (event) => {
                    try {
                        const message = JSON.parse(event.data);
                        log(`Otrzymano wiadomość: ${JSON.stringify(message, null, 2)}`, 'received');
                    } catch (error) {
                        log(`Otrzymano wiadomość: ${event.data}`, 'received');
                    }
                };
                
                socket.onclose = (event) => {
                    log(`Rozłączono z serwerem WebSocket: kod ${event.code}, powód: ${event.reason || 'brak'}`);
                    updateStatus(false);
                };
                
                socket.onerror = (error) => {
                    log(`Błąd WebSocket: ${error.message || 'nieznany błąd'}`, 'error');
                };
            } catch (error) {
                log(`Błąd podczas łączenia: ${error.message}`, 'error');
            }
        }
        
        // Funkcja rozłączająca z serwerem WebSocket
        function disconnect() {
            if (socket) {
                log('Rozłączanie z serwerem WebSocket...');
                socket.close();
                socket = null;
            }
        }
        
        // Funkcja wysyłająca wiadomość ping
        function sendPing() {
            if (socket && isConnected) {
                const message = {
                    type: 'ping',
                    timestamp: Date.now()
                };
                log(`Wysyłanie ping: ${JSON.stringify(message)}`);
                socket.send(JSON.stringify(message));
            }
        }
        
        // Funkcja symulująca autoryzację
        function simulateAuth() {
            if (socket && isConnected) {
                const message = {
                    type: 'auth',
                    token: 'test_token_123'
                };
                log(`Wysyłanie autoryzacji: ${JSON.stringify(message)}`);
                socket.send(JSON.stringify(message));
            }
        }
        
        // Funkcja wysyłająca pozycję
        function sendPosition() {
            if (socket && isConnected) {
                const message = {
                    type: 'position_update',
                    position: {
                        lat: 54.352 + (Math.random() * 0.01),
                        lng: 18.646 + (Math.random() * 0.01)
                    },
                    speed: Math.random() * 10,
                    distance: Math.random() * 1000
                };
                log(`Wysyłanie pozycji: ${JSON.stringify(message)}`);
                socket.send(JSON.stringify(message));
            }
        }
        
        // Obsługa przycisków
        connectBtn.addEventListener('click', connect);
        disconnectBtn.addEventListener('click', disconnect);
        pingBtn.addEventListener('click', sendPing);
        authBtn.addEventListener('click', simulateAuth);
        positionBtn.addEventListener('click', sendPosition);
        
        // Inicjalizacja
        log('Strona testowa WebSocket załadowana');
        log('Kliknij "Połącz", aby nawiązać połączenie z serwerem WebSocket');
    </script>
</body>
</html>
""")
        logger.info(f"Plik testowy utworzony. Otwieranie przeglądarki: {test_url}")
        webbrowser.open(test_url)
    
    # Wyświetl instrukcje
    logger.info("\n=== Instrukcje testowe ===")
    logger.info("1. W przeglądarce kliknij przycisk 'Połącz', aby nawiązać połączenie WebSocket")
    logger.info("2. Sprawdź, czy status zmienia się na 'Połączony'")
    logger.info("3. Użyj przycisków do testowania różnych funkcji:")
    logger.info("   - 'Wyślij Ping' - wysyła wiadomość ping do serwera")
    logger.info("   - 'Symuluj Autoryzację' - symuluje proces autoryzacji")
    logger.info("   - 'Wyślij Pozycję' - wysyła przykładową pozycję GPS")
    logger.info("4. Obserwuj logi w przeglądarce i w konsoli")
    logger.info("\nNaciśnij Ctrl+C, aby zakończyć test\n")
    
    try:
        # Czekaj na zakończenie przez użytkownika
        await websocket_task
    except asyncio.CancelledError:
        logger.info("Test zakończony")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nTest przerwany przez użytkownika")
    except Exception as e:
        logger.error(f"\nWystąpił nieoczekiwany błąd: {e}")
