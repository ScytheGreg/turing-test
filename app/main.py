from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.conversation.controller import ConversationController
from app.realtime.manager import ConnectionManager


class MessageRequest(BaseModel):
    text: str


app = FastAPI(title="Turing Test")


@app.middleware("http")
async def disable_frontend_cache(request: Request, call_next):
    response = await call_next(request)

    if request.url.path.startswith(("/participant", "/display")):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

    return response


connection_manager = ConnectionManager()
controllers: dict[str, ConversationController] = {
    "alice": ConversationController(),
    "bob": ConversationController(),
}


def get_controller(session_id: str) -> ConversationController:
    sid = session_id.lower()
    if sid not in controllers:
        raise HTTPException(
            status_code=404,
            detail=f"Nieznana sesja: {session_id}. Dostępne: alice, bob",
        )
    return controllers[sid]


BASE_DIR = Path(__file__).resolve().parent.parent
PARTICIPANT_DIR = BASE_DIR / "frontend" / "participant"
DISPLAY_DIR = BASE_DIR / "frontend" / "display"
HUMAN_DIR = BASE_DIR / "frontend" / "human"

app.mount(
    "/participant",
    StaticFiles(directory=PARTICIPANT_DIR, html=True),
    name="participant",
)
app.mount(
    "/display",
    StaticFiles(directory=DISPLAY_DIR, html=True),
    name="display",
)
app.mount(
    "/human",
    StaticFiles(directory=HUMAN_DIR, html=True),
    name="human",
)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(PARTICIPANT_DIR / "index.html")


@app.get("/karty.pdf")
def get_karty_pdf() -> FileResponse:
    return FileResponse(BASE_DIR / "karty.pdf", media_type="application/pdf")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/session/{session_id}/message")
async def send_message(session_id: str, data: MessageRequest) -> dict[str, str]:
    ctrl = get_controller(session_id)

    try:
        answer = ctrl.send(data.text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    await connection_manager.send_to_session(
        session_id.lower(),
        {
            "type": "assistant_message",
            "session_id": session_id.lower(),
            "text": answer,
        },
    )

    return {"answer": answer}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
) -> None:
    normalized_session_id = session_id.lower()
    await connection_manager.connect(normalized_session_id, websocket)

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "session_id": normalized_session_id,
            }
        )

        while True:
            data = await websocket.receive_json()
            text = str(data.get("text", "")).strip()

            if not text:
                continue

            message_type = data.get("type", "user_message")
            if message_type == "human_reply":
                if normalized_session_id != "bob":
                    continue

                await connection_manager.send_to_session(
                    normalized_session_id,
                    {
                        "type": "human_reply",
                        "session_id": normalized_session_id,
                        "text": text,
                    },
                )
                continue

            await connection_manager.send_to_session(
                normalized_session_id,
                {
                    "type": "user_message",
                    "session_id": normalized_session_id,
                    "text": text,
                    "sender": "host",
                },
            )

    except WebSocketDisconnect:
        connection_manager.disconnect(normalized_session_id, websocket)
