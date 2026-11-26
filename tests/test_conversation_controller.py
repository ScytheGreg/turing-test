import pytest

from app.conversation.controller import ConversationController


class FakeConversation:
    def __init__(self) -> None:
        self.sent_messages: list[str] = []

    def send(self, message: str) -> str:
        self.sent_messages.append(message)
        return "Odpowiedź AI."


def test_send_forwards_typed_text_and_returns_answer():
    conversation = FakeConversation()
    controller = ConversationController(conversation=conversation)

    answer = controller.send("  Wiadomość wpisana ręcznie.  ")

    assert answer == "Odpowiedź AI."
    assert conversation.sent_messages == ["Wiadomość wpisana ręcznie."]


def test_send_rejects_empty_text_from_conversation_service():
    class RejectEmptyConversation(FakeConversation):
        def send(self, message: str) -> str:
            if not message:
                raise ValueError("Wiadomość użytkownika nie może być pusta.")
            return super().send(message)

    controller = ConversationController(conversation=RejectEmptyConversation())

    with pytest.raises(ValueError, match="nie może być pusta"):
        controller.send("   ")
