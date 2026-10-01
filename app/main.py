from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from pathlib import Path

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.conversation.controller import ConversationController

import os

class TranscriptUpdate(BaseModel):
    text: str
app = FastAPI(title="Turing Test")

controller = ConversationController()

BASE_DIR = Path(__file__).resolve().parent.parent
PARTICIPANT_DIR = BASE_DIR / "frontend" / "participant"

# Pobieramy rodzica pliku wav z controller.audio_path lub folder wyżej
# Jeśli controller zapisuje w tempfile.gettempdir(), używamy rodzica z audio_path
if controller.audio_path:
    AUDIO_DIR = Path(controller.audio_path).parent
else:
    import tempfile
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


@app.get("/api/state")
def get_state() -> dict[str, str | None]:
    return {
        "state": controller.state.value,
        "transcript": controller.transcript,
        "answer": controller.answer,
    }


@app.post("/api/record/start")
def start_recording() -> dict[str, str]:
    try:
        controller.start_recording()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        "state": controller.state.value,
    }


@app.post("/api/record/stop")
def stop_recording() -> dict[str, str]:
    try:
        transcript = controller.stop_recording()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        "state": controller.state.value,
        "transcript": transcript,
    }

@app.post("/api/send")
def send_message() -> dict[str, str | None]:
    try:
        answer = controller.send()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    # Konwersja ścieżki pliku na URL dla przeglądarki (/audio/nazwa_pliku.wav)
    audio_url = None
    if controller.audio_path is not None:
        filename = Path(controller.audio_path).name
        audio_url = f"/audio/{filename}"

    return {
        "state": controller.state.value,
        "answer": answer,
        "audio_path": audio_url,  # Zwracamy czysty URL dla frontendu
    }

@app.put("/api/transcript")
def update_transcript(data: TranscriptUpdate) -> dict[str, str | None]:
    try:
        controller.edit_transcript(data.text)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return {
        "state": controller.state.value,
        "transcript": controller.transcript,
    }

@app.post("/api/cancel")
def cancel() -> dict[str, str | None]:
    controller.cancel()

    return {
        "state": controller.state.value,
        "transcript": controller.transcript,
        "answer": controller.answer,
    }