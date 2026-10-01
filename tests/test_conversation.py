from app.conversation.service import ConversationService


class FakeLLM:
    def __init__(self) -> None:
        self.received_messages = []

    def chat_with_history(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        self.received_messages.append(messages.copy())
        return "To jest odpowiedź testowa."


def test_conversation_keeps_history():
    llm = FakeLLM()
    conversation = ConversationService(llm)

    answer1 = conversation.send("Cześć!")
    answer2 = conversation.send("Jak masz na imię?")

    assert answer1 == "To jest odpowiedź testowa."
    assert answer2 == "To jest odpowiedź testowa."

    assert conversation.messages == [
        {"role": "system", "content": "Odpowiadaj krótko po polsku."},
        {"role": "user", "content": "Cześć!"},
        {"role": "assistant", "content": "To jest odpowiedź testowa."},
        {"role": "user", "content": "Jak masz na imię?"},
        {"role": "assistant", "content": "To jest odpowiedź testowa."},
    ]


def test_conversation_rejects_empty_message():
    conversation = ConversationService(FakeLLM())

    try:
        conversation.send("   ")
        assert False
    except ValueError:
        pass


def test_reset_clears_conversation():
    conversation = ConversationService(FakeLLM())

    conversation.send("Cześć!")
    conversation.reset()

    assert conversation.messages == [
        {"role": "system", "content": "Odpowiadaj krótko po polsku."},
    ]
