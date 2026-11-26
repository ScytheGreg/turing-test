import asyncio

import httpx
from fastapi import WebSocketDisconnect

import app.main as main
from app.conversation.controller import ConversationController


class FakeConversation:
    def __init__(self) -> None:
        self.sent_messages: list[str] = []

    def send(self, message: str) -> str:
        if not message.strip():
            raise ValueError("Wiadomość użytkownika nie może być pusta.")

        self.sent_messages.append(message)
        return "Odpowiedź testowa."


class FakeWebSocket:
    def __init__(self, incoming_messages: list[dict[str, str]]) -> None:
        self.incoming_messages = iter(incoming_messages)
        self.sent_messages: list[dict] = []

    async def accept(self) -> None:
        pass

    async def send_json(self, message: dict) -> None:
        self.sent_messages.append(message)

    async def receive_json(self) -> dict[str, str]:
        try:
            return next(self.incoming_messages)
        except StopIteration:
            raise WebSocketDisconnect(code=1000)


def test_alice_can_send_typed_message(monkeypatch):
    conversation = FakeConversation()
    monkeypatch.setitem(
        main.controllers,
        "alice",
        ConversationController(conversation=conversation),
    )

    async def exercise() -> httpx.Response:
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.post(
                "/api/session/alice/message",
                json={"text": "Wiadomość wpisana ręcznie."},
            )

    response = asyncio.run(exercise())

    assert response.status_code == 200
    assert response.json() == {"answer": "Odpowiedź testowa."}
    assert conversation.sent_messages == ["Wiadomość wpisana ręcznie."]


def test_message_endpoint_rejects_empty_text(monkeypatch):
    monkeypatch.setitem(
        main.controllers,
        "alice",
        ConversationController(conversation=FakeConversation()),
    )

    async def exercise() -> httpx.Response:
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.post(
                "/api/session/alice/message",
                json={"text": "   "},
            )

    response = asyncio.run(exercise())

    assert response.status_code == 422


def test_bob_websocket_broadcasts_host_and_human_text():
    websocket = FakeWebSocket(
        [
            {"text": "Pytanie prowadzącego."},
            {"type": "human_reply", "text": "Odpowiedź człowieka."},
        ]
    )

    asyncio.run(main.websocket_endpoint(websocket, "bob"))

    assert websocket.sent_messages == [
        {"type": "connected", "session_id": "bob"},
        {
            "type": "user_message",
            "session_id": "bob",
            "text": "Pytanie prowadzącego.",
            "sender": "host",
        },
        {
            "type": "human_reply",
            "session_id": "bob",
            "text": "Odpowiedź człowieka.",
        },
    ]
