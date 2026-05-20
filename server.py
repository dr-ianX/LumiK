import asyncio
import http.server
import socketserver
import websockets
import json
import os
from pathlib import Path

# Configuration - OnRender compatible
PORT = int(os.environ.get("PORT", 3001))
DATA_DIR = Path("data")
HOST = "0.0.0.0"  # Listen on all interfaces for OnRender

# WebSocket connections
connected_clients = set()

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DATA_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def translate_path(self, path):
        # Serve control.html as default for root
        if path == "/":
            return str(DATA_DIR / "control.html")
        elif path == "/assistant":
            return str(DATA_DIR / "assistant.html")
        elif path == "/chat":
            return str(DATA_DIR / "chat.html")
        elif path == "/favicon.ico":
            return str(DATA_DIR / "favicon.ico")
        else:
            return super().translate_path(path)

async def websocket_handler(websocket, path):
    # Add client to connected clients
    connected_clients.add(websocket)
    print(f"Cliente conectado: {websocket.remote_address}")

    try:
        async for message in websocket:
            # Echo message to all connected clients
            if connected_clients:
                await asyncio.gather(
                    *[client.send(message) for client in connected_clients if client != websocket]
                )
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Remove client from connected clients
        if websocket in connected_clients:
            connected_clients.remove(websocket)
        print(f"Cliente desconectado: {websocket.remote_address}")

async def start_websocket_server():
    async with websockets.serve(websocket_handler, HOST, PORT, subprotocols=None):
        print(f"Servidor WebSocket iniciado en ws://{HOST}:{PORT}/ws")
        await asyncio.Future()  # Run forever

def start_http_server():
    with socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Servidor HTTP iniciado en http://{HOST}:{PORT}")
        print("Sirviendo archivos desde el directorio 'data'")
        print(f" - Página principal (Control): http://{HOST}:{PORT}/")
        print(f" - Página de asistente: http://{HOST}:{PORT}/assistant")
        httpd.serve_forever()

if __name__ == "__main__":
    # Start both servers
    import threading

    # Start WebSocket server in a separate thread
    ws_thread = threading.Thread(target=lambda: asyncio.run(start_websocket_server()))
    ws_thread.daemon = True
    ws_thread.start()

    # Start HTTP server in the main thread
    start_http_server()
