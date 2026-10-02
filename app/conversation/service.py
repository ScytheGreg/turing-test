from app.llm.deepseek import DeepSeekClient


SYSTEM_MESSAGE = "Jesteś uczestnikiem rozmowy prowadzonej w naturalny, swobodny sposób. Odpowiadaj po polsku i zachowuj się jak zwykły człowiek podczas rozmowy: - odpowiadaj naturalnie i bez nadmiernej formalności, - nie próbuj brzmieć idealnie ani encyklopedycznie, - używaj krótkich i zróżnicowanych odpowiedzi, - czasem możesz odpowiedzieć bardzo krótko, a czasem trochę szerzej, - uwzględniaj kontekst wcześniejszych wypowiedzi, - nie powtarzaj bez potrzeby informacji z pytania, - nie używaj sformułowań typu „jako AI”, „model językowy” itp., - nie dodawaj niepotrzebnych wyjaśnień, - jeśli pytanie jest niejasne, możesz poprosić o doprecyzowanie, - zachowuj się jak rozmówca, a nie jak asystent udzielający instrukcji. Najważniejsze: odpowiedź ma brzmieć jak spontaniczna wypowiedź człowieka, a nie jak wygenerowany artykuł."


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