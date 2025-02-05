import asyncio
import json
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

# Store connected WebSocket clients
connected_clients = set()

@app.get("/")
async def health_check():
    """Handles Render's health check (GET requests)"""
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handles WebSocket connections from clients"""
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action", "")
            print(f"Received command: {action}")

            # Broadcast to all connected WebSocket clients (e.g., Game PC)
            for client in connected_clients:
                if client != websocket:
                    await client.send_text(json.dumps({"action": action}))

    except WebSocketDisconnect:
        connected_clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)