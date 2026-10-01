import pytest

from app.conversation.service import ConversationService


@pytest.mark.integration
def test_real_conversation():
    conversation = ConversationService()

    answer1 = conversation.send("Cześć! Odpowiedz jednym krótkim zdaniem.")
    answer2 = conversation.send("A teraz powiedz, co przed chwilą zrobiłem.")

    assert answer1
    assert answer2

    print("\n=== ODPOWIEDŹ 1 ===")
    print(answer1)

    print("\n=== ODPOWIEDŹ 2 ===")
    print(answer2)
