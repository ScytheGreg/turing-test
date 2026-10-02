from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(
        self,
        session_id: str,
        websocket: WebSocket,
    ) -> None:
        await websocket.accept()
        self.connections[session_id].append(websocket)

    def disconnect(
        self,
        session_id: str,
        websocket: WebSocket,
    ) -> None:
        connections = self.connections.get(session_id)

        if not connections:
            return

        if websocket in connections:
            connections.remove(websocket)

        if not connections:
            del self.connections[session_id]

    async def send_to_session(
        self,
        session_id: str,
        message: dict,
    ) -> None:
        connections = self.connections.get(session_id, [])

        for websocket in connections:
            await websocket.send_json(message)