from fastapi import FastAPI, HTTPException

from app.conversation.controller import ConversationController

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