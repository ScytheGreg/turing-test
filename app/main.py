import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.conversation.controller import ConversationController
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from app.realtime.manager import ConnectionManager
from app.tts.piper import PiperTTS
import asyncio


class TranscriptUpdate(BaseModel):
    text: str

async def ai_sleep(ansLen: int):
    await asyncio.sleep(max(ansLen / 8, 4))

app = FastAPI(title="Turing Test")


@app.middleware("http")
async def disable_frontend_cache(request: Request, call_next):
    response = await call_next(request)

    if request.url.path.startswith(("/participant", "/display")):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"

    return response

connection_manager = ConnectionManager()
tts = PiperTTS()

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
DISPLAY_DIR = BASE_DIR / "frontend" / "display"
HUMAN_DIR = BASE_DIR / "frontend" / "human"

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

app.mount(
    "/display",
    StaticFiles(
        directory=DISPLAY_DIR,
        html=True,
    ),
    name="display",
)

app.mount(
    "/human",
    StaticFiles(
        directory=HUMAN_DIR,
        html=True,
    ),
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
async def send_message(session_id: str) -> dict[str, str | None]:
    ctrl = get_controller(session_id)

    transcript = ctrl.transcript

    if not transcript:
        raise HTTPException(
            status_code=409,
            detail="Brak transkrypcji do wysłania.",
        )

    await asyncio.sleep(2) # Czas na załadowanie głosu i przeczytanie przez lektora

    # Dopiero teraz pytamy LLM i generujemy odpowiedź Alice.
    try:
        answer = ctrl.send()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    audio_url = None

    await ai_sleep(len(answer))

    if ctrl.audio_path is not None:
        filename = Path(ctrl.audio_path).name
        audio_url = f"/audio/{filename}"

    # Odpowiedź Alice pojawia się na display.
    await connection_manager.send_to_session(
        session_id,
        {
            "type": "assistant_message",
            "session_id": session_id,
            "text": answer,
        },
    )

    # Głos Alice.
    await connection_manager.send_to_session(
        session_id,
        {
            "type": "audio_ready",
            "session_id": session_id,
            "audio_url": audio_url,
            "voice": "alice",
        },
    )

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
            message_type = data.get("type", "user_message")

            if message_type == "human_reply":
                if session_id.lower() != "bob":
                    continue

                audio_path = tts.synthesize(
                    text,
                    voice="bob",
                )

                filename = Path(audio_path).name
                audio_url = f"/audio/{filename}"

                await connection_manager.send_to_session(
                    session_id,
                    {
                        "type": "human_reply",
                        "session_id": session_id,
                        "text": text,
                    },
                )

                await connection_manager.send_to_session(
                    session_id,
                    {
                        "type": "audio_ready",
                        "session_id": session_id,
                        "audio_url": audio_url,
                        "voice": "bob",
                    },
                )

                continue

            await connection_manager.send_to_session(
                session_id,
                {
                    "type": "user_message",
                    "session_id": session_id,
                    "text": text,
                    "sender": "host",
                },
            )

            # Głos prowadzącego generujemy dla obu rozmów.
            audio_path = tts.synthesize(
                text,
                voice="host",
            )

            filename = Path(audio_path).name
            audio_url = f"/audio/{filename}"

            await connection_manager.send_to_session(
                session_id,
                {
                    "type": "audio_ready",
                    "session_id": session_id,
                    "audio_url": audio_url,
                    "voice": "host",
                },
            )

    except WebSocketDisconnect:
        connection_manager.disconnect(
            session_id,
            websocket,
        )
