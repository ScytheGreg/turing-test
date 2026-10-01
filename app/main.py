from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.conversation.controller import ConversationController

class TranscriptUpdate(BaseModel):
    text: str
app = FastAPI(title="Turing Test")

controller = ConversationController()


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

    return {
        "state": controller.state.value,
        "answer": answer,
        "audio_path": (
            str(controller.audio_path)
            if controller.audio_path is not None
            else None
        ),
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