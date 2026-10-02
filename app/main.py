import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.conversation.controller import ConversationController
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from app.realtime.manager import ConnectionManager


class TranscriptUpdate(BaseModel):
    text: str


app = FastAPI(title="Turing Test")

connection_manager = ConnectionManager()

# Słownik przechowujący osobne kontrolery dla Alice i Boba
controllers: dict[str, ConversationController] = {
    "alice": ConversationController(),
    "bob": ConversationController(),
}


def get_controller(session_id: str) -> ConversationController:
    sid = session_id.lower()
    if sid not in controllers:
        raise HTTPException(
            status_code=404,
            detail=f"Nieznana sesja: {session_id}. Dostępne: alice, bob"
        )
    return controllers[sid]


BASE_DIR = Path(__file__).resolve().parent.parent
PARTICIPANT_DIR = BASE_DIR / "frontend" / "participant"

# Domyślny folder dla audio (będzie obsługiwać pliki tymczasowe)
AUDIO_DIR = Path(tempfile.gettempdir())
app.mount("/audio", StaticFiles(directory=str(AUDIO_DIR)), name="audio")

app.mount(
    "/participant",
    StaticFiles(
        directory=PARTICIPANT_DIR,
        html=True,
    ),
    name="participant",
)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(PARTICIPANT_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/session/{session_id}/state")
def get_state(session_id: str) -> dict[str, str | None]:
    ctrl = get_controller(session_id)
    return {
        "state": ctrl.state.value,
        "transcript": ctrl.transcript,
        "answer": ctrl.answer,
    }


@app.post("/api/session/{session_id}/record/start")
def start_recording(session_id: str) -> dict[str, str]:
    ctrl = get_controller(session_id)
    try:
        ctrl.start_recording()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        "state": ctrl.state.value,
    }


@app.post("/api/session/{session_id}/record/stop")
def stop_recording(session_id: str) -> dict[str, str]:
    ctrl = get_controller(session_id)
    try:
        transcript = ctrl.stop_recording()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        "state": ctrl.state.value,
        "transcript": transcript,
    }


@app.post("/api/session/{session_id}/send")
def send_message(session_id: str) -> dict[str, str | None]:
    ctrl = get_controller(session_id)
    try:
        answer = ctrl.send()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    # Konwersja ścieżki pliku na URL dla przeglądarki (/audio/nazwa_pliku.wav)
    audio_url = None
    if ctrl.audio_path is not None:
        filename = Path(ctrl.audio_path).name
        audio_url = f"/audio/{filename}"

    return {
        "state": ctrl.state.value,
        "answer": answer,
        "audio_path": audio_url,
    }


@app.put("/api/session/{session_id}/transcript")
def update_transcript(session_id: str, data: TranscriptUpdate) -> dict[str, str | None]:
    ctrl = get_controller(session_id)
    try:
        ctrl.edit_transcript(data.text)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        "state": ctrl.state.value,
        "transcript": ctrl.transcript,
    }


@app.post("/api/session/{session_id}/cancel")
def cancel(session_id: str) -> dict[str, str | None]:
    ctrl = get_controller(session_id)
    ctrl.cancel()

    return {
        "state": ctrl.state.value,
        "transcript": ctrl.transcript,
        "answer": ctrl.answer,
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
) -> None:
    await connection_manager.connect(session_id, websocket)

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "session_id": session_id,
            }
        )

        while True:
            data = await websocket.receive_json()

            text = str(data.get("text", "")).strip()

            if not text:
                continue

            await connection_manager.send_to_session(
                session_id,
                {
                    "type": "user_message",
                    "session_id": session_id,
                    "text": text,
                },
            )

    except WebSocketDisconnect:
        connection_manager.disconnect(
            session_id,
            websocket,
        )