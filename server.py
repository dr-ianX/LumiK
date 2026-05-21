import asyncio
import websockets
import json
import os
from pathlib import Path
from aiohttp import web, WSMsgType

# Configuration - OnRender compatible
PORT = int(os.environ.get("PORT", 3001))
DATA_DIR = Path("data")
UPLOADS_DIR = DATA_DIR / "uploads"
HOST = "0.0.0.0"  # Listen on all interfaces for OnRender

# Create uploads directory if it doesn't exist
UPLOADS_DIR.mkdir(exist_ok=True)

# WebSocket connections
connected_clients = set()

async def handle_websocket(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    connected_clients.add(ws)
    print(f"Cliente conectado: {request.remote}")
    
    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                # Echo message to all connected clients
                if connected_clients:
                    await asyncio.gather(
                        *[client.send_str(msg.data) for client in connected_clients if client != ws]
                    )
            elif msg.type == WSMsgType.ERROR:
                print(f"WebSocket error: {ws.exception()}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if ws in connected_clients:
            connected_clients.remove(ws)
        print(f"Cliente desconectado: {request.remote}")
    
    return ws

async def handle_upload(request):
    print(f"Upload request received. Method: {request.method}")
    if request.method == 'POST':
        try:
            reader = await request.multipart()
            
            async for field in reader:
                if field.name == 'audio':
                    filename = field.filename
                    if not filename:
                        return web.Response(status=400, text="No filename provided")
                    
                    # Generate unique filename
                    import uuid
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    file_path = UPLOADS_DIR / unique_filename
                    
                    # Save file
                    with open(file_path, 'wb') as f:
                        while True:
                            chunk = await field.read_chunk()
                            if not chunk:
                                break
                            f.write(chunk)
                    
                    print(f"Archivo subido: {unique_filename}")
                    
                    # Return the URL to access the file
                    file_url = f"/uploads/{unique_filename}"
                    return web.json_response({'url': file_url})
            
            return web.Response(status=400, text="No audio file provided")
        except Exception as e:
            print(f"Error en upload: {e}")
            return web.Response(status=500, text=f"Error uploading file: {e}")
    
    print(f"Method not allowed: {request.method}")
    return web.Response(status=405, text="Method not allowed")

async def handle_upload_favicon(request):
    print(f"Favicon upload request received. Method: {request.method}")
    if request.method == 'POST':
        try:
            reader = await request.multipart()
            
            async for field in reader:
                if field.name == 'favicon':
                    filename = field.filename
                    if not filename:
                        return web.Response(status=400, text="No filename provided")
                    
                    # Generate unique filename
                    import uuid
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    file_path = UPLOADS_DIR / unique_filename
                    
                    # Save file
                    with open(file_path, 'wb') as f:
                        while True:
                            chunk = await field.read_chunk()
                            if not chunk:
                                break
                            f.write(chunk)
                    
                    print(f"Favicon subido: {unique_filename}")
                    
                    # Return the URL to access the file
                    file_url = f"/uploads/{unique_filename}"
                    return web.json_response({'url': file_url})
            
            return web.Response(status=400, text="No favicon file provided")
        except Exception as e:
            print(f"Error en favicon upload: {e}")
            return web.Response(status=500, text=f"Error uploading favicon: {e}")
    
    print(f"Method not allowed: {request.method}")
    return web.Response(status=405, text="Method not allowed")

async def handle_request(request):
    path = request.path
    print(f"Request received: {path}, Method: {request.method}")
    
    # Handle upload endpoint - must be before file serving
    if path == "/upload":
        return await handle_upload(request)
    
    # Handle favicon upload endpoint
    if path == "/upload-favicon":
        print("Routing to handle_upload_favicon")
        return await handle_upload_favicon(request)
    
    # Determine which file to serve
    if path == "/":
        file_path = DATA_DIR / "control.html"
    elif path == "/assistant":
        file_path = DATA_DIR / "assistant.html"
    elif path == "/chat":
        file_path = DATA_DIR / "chat.html"
    elif path == "/favicon.ico":
        file_path = DATA_DIR / "favicon.ico"
    elif path.startswith("/uploads/"):
        file_path = UPLOADS_DIR / path.lstrip("/uploads/")
    else:
        file_path = DATA_DIR / path.lstrip("/")
    
    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        return web.Response(status=404, text="File not found")
    
    # Read and serve file
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Set content type based on file extension
        content_type = 'text/html'
        if file_path.suffix == '.css':
            content_type = 'text/css'
        elif file_path.suffix == '.js':
            content_type = 'application/javascript'
        elif file_path.suffix == '.ico':
            content_type = 'image/x-icon'
        elif file_path.suffix in ['.mp3', '.wav', '.ogg', '.m4a']:
            content_type = 'audio/mpeg'
        
        response = web.Response(body=content, content_type=content_type)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
    except Exception as e:
        return web.Response(status=500, text=f"Error serving file: {e}")

async def start_server():
    app = web.Application()
    
    # WebSocket route
    app.add_routes([web.get('/ws', handle_websocket)])
    
    # POST routes for uploads
    app.add_routes([web.post('/upload', handle_upload)])
    app.add_routes([web.post('/upload-favicon', handle_upload_favicon)])
    
    # HTTP routes (catch-all for static files)
    app.add_routes([web.get('/', handle_request)])
    app.add_routes([web.get('/{path:.*}', handle_request)])
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()
    
    print(f"Servidor iniciado en http://{HOST}:{PORT}")
    print("Sirviendo archivos desde el directorio 'data'")
    print(f" - Página principal (Control): http://{HOST}:{PORT}/")
    print(f" - Página de asistente: http://{HOST}:{PORT}/assistant")
    print(f" - Página de chat: http://{HOST}:{PORT}/chat")
    print(f" - WebSocket: ws://{HOST}:{PORT}/ws")
    
    # Keep server running
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        pass
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(start_server())
