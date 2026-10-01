from app.llm.deepseek import DeepSeekClient


SYSTEM_MESSAGE = "Odpowiadaj krótko po polsku."


class ConversationService:
    def __init__(self, llm: DeepSeekClient | None = None) -> None:
        self.llm = llm or DeepSeekClient()
        self.messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": SYSTEM_MESSAGE,
            }
        ]

    def send(self, user_message: str) -> str:
        if not user_message.strip():
            raise ValueError("Wiadomość użytkownika nie może być pusta.")

        self.messages.append(
            {
                "role": "user",
                "content": user_message,
            }
        )

        answer = self.llm.chat_with_history(self.messages)

        self.messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        return answer

    def reset(self) -> None:
        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_MESSAGE,
            }
        ]