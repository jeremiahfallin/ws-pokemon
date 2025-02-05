import asyncio
import websockets
import json

connected_clients = set()

async def handle_connection(websocket, path):
    # Register the new client
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            action = data.get("action", "")
            print(f"Received command: {action}")

            # Broadcast the command to all connected clients (Game PC)
            await asyncio.gather(*[client.send(json.dumps({"action": action})) for client in connected_clients if client != websocket])

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Remove client when disconnected
        connected_clients.remove(websocket)

async def start_server():
    async with websockets.serve(handle_connection, "0.0.0.0", 5000):
        print("WebSocket server running on port 5000")
        await asyncio.Future()  # Keep the server running

if __name__ == "__main__":
    asyncio.run(start_server())