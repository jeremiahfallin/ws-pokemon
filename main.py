import asyncio
import websockets
import json
from http.server import SimpleHTTPRequestHandler
import socketserver
import threading

connected_clients = set()

async def handle_connection(websocket, path):
    """Handle incoming WebSocket connections and broadcast messages."""
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action", "")
            print(f"Received command: {action}")

            # Broadcast command to all connected clients (e.g., Game PC)
            await asyncio.gather(
                *[client.send(json.dumps({"action": action})) for client in connected_clients if client != websocket]
            )

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Remove disconnected client
        connected_clients.remove(websocket)

async def start_websocket_server():
    """Start the WebSocket server on port 5000."""
    async with websockets.serve(handle_connection, "0.0.0.0", 5000):
        print("WebSocket server running on ws://0.0.0.0:5000")
        await asyncio.Future()  # Keep the server running

class HealthCheckHandler(SimpleHTTPRequestHandler):
    """Handles Render's health check requests by responding with 200 OK."""
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()

def start_http_server():
    """Run a simple HTTP server for Render health checks on port 8080."""
    with socketserver.TCPServer(("", 8080), HealthCheckHandler) as httpd:
        print("Health check server running on port 8080")
        httpd.serve_forever()

if __name__ == "__main__":
    # Start the HTTP health check server in a separate thread
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    # Start the WebSocket server
    asyncio.run(start_websocket_server())