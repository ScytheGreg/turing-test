from app.conversation.service import ConversationService


class ConversationController:
    def __init__(self, conversation: ConversationService | None = None) -> None:
        self.conversation = conversation or ConversationService()

    def send(self, text: str) -> str:
        return self.conversation.send(text.strip())
