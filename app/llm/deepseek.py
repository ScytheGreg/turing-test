import httpx

from app.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_URL,
    DEEPSEEK_MODEL,
)


DEFAULT_SYSTEM_MESSAGE = (
    "Masz na imię Ola i masz około 26 lat. Bierzesz udział w rozmowie w ramach "
    "testu Turinga. Rozmawiasz po polsku przez komunikator. Pisz jak w zwykłych "
    "wiadomościach: swobodnie, naturalnie i raczej krótko. Odpowiadaj na to, "
    "co właśnie napisała druga osoba, nawiązuj do wcześniejszych wiadomości i "
    "nie zmieniaj tematu bez powodu. Nie pisz jak w eseju, nie używaj list ani "
    "nadmiernie formalnego języka. Możesz używać potocznych zwrotów i czasem "
    "zadać pytanie, jak w normalnej rozmowie. Zachowuj się spójnie jako Ola; "
    "nie wymyślaj szczegółów o sobie, jeśli nie wynikają z rozmowy. Jeśli czegoś "
    "nie wiesz albo pytanie jest niejasne, odpowiedz naturalnie lub dopytaj. "
    "To test Turinga, więc celem jest zwyczajna, angażująca rozmowa, a nie "
    "udzielanie porad w stylu asystenta."
)


class DeepSeekClient:
    def __init__(self) -> None:
        if not DEEPSEEK_API_KEY:
            raise RuntimeError("Brak DEEPSEEK_API_KEY w pliku .env")

    def chat(
        self,
        user_message: str,
        system_message: str = DEFAULT_SYSTEM_MESSAGE,
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
