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
        system_message: str = "Odpowiadaj krótko po polsku.",
    ) -> str:
        response = httpx.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": system_message,
                    },
                    {
                        "role": "user",
                        "content": user_message,
                    },
                ],
                "stream": False,
            },
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"].strip()
