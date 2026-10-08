import asyncio
from pathlib import Path

import httpx

import app.main as main
from app.conversation.controller import ConversationController


class FakeConversation:
    def __init__(self) -> None:
        self.sent_messages: list[str] = []

    def send(self, message: str) -> str:
        self.sent_messages.append(message)
        return "Odpowiedź testowa."


class FakeTTS:
    def __init__(self, path: Path) -> None:
        self.path = path

    def synthesize(self, text: str) -> Path:
        self.path.touch()
        return self.path


def test_alice_can_send_text_without_recording(monkeypatch, tmp_path):
    conversation = FakeConversation()
    audio_path = tmp_path / "answer.wav"
    controller = ConversationController(
        recorder=object(),
        stt=object(),
        conversation=conversation,
        tts=FakeTTS(audio_path),
    )
    monkeypatch.setitem(main.controllers, "alice", controller)

    async def exercise() -> tuple[httpx.Response, httpx.Response]:
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            transcript_response = await client.put(
                "/api/session/alice/transcript",
                json={"text": "Wiadomość bez nagrania."},
            )
            send_response = await client.post("/api/session/alice/send")
            return transcript_response, send_response

    transcript_response, send_response = asyncio.run(exercise())

    assert transcript_response.status_code == 200
    assert send_response.status_code == 200
    assert conversation.sent_messages == ["Wiadomość bez nagrania."]
    assert send_response.json()["answer"] == "Odpowiedź testowa."
