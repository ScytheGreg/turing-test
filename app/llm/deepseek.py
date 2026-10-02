import httpx

from app.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_URL,
    DEEPSEEK_MODEL,
)


class DeepSeekClient:
    def __init__(self) -> None:
        if not DEEPSEEK_API_KEY:
            raise RuntimeError("Brak DEEPSEEK_API_KEY w pliku .env")

    def chat(
        self,
        user_message: str,
        system_message: str = "Jesteś uczestnikiem rozmowy prowadzonej w naturalny, swobodny sposób. Odpowiadaj po polsku i zachowuj się jak zwykły człowiek podczas rozmowy: - odpowiadaj naturalnie i bez nadmiernej formalności, - nie próbuj brzmieć idealnie ani encyklopedycznie, - używaj krótkich i zróżnicowanych odpowiedzi, - czasem możesz odpowiedzieć bardzo krótko, a czasem trochę szerzej, - uwzględniaj kontekst wcześniejszych wypowiedzi, - nie powtarzaj bez potrzeby informacji z pytania, - nie używaj sformułowań typu „jako AI”, „model językowy” itp., - nie dodawaj niepotrzebnych wyjaśnień, - jeśli pytanie jest niejasne, możesz poprosić o doprecyzowanie, - zachowuj się jak rozmówca, a nie jak asystent udzielający instrukcji. Najważniejsze: odpowiedź ma brzmieć jak spontaniczna wypowiedź człowieka, a nie jak wygenerowany artykuł.",
    ) -> str:
        messages = [
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]

        return self.chat_with_history(messages)

    def chat_with_history(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        response = httpx.post(
          DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": messages,
                "stream": False,
            },
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"].strip()