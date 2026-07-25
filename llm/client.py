import base64

import httpx

from config import settings


class OpenRouterClient:
    def __init__(self) -> None:
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1"

    def transcribe(self, mp3_bytes: bytes) -> str:
        content = [
            {
                "type": "text",
                "text": "Расшифруй голосовое сообщение дословно, по-русски. "
                "В ответе — только текст расшифровки, без комментариев.",
            },
            {
                "type": "input_audio",
                "input_audio": {
                    "data": base64.b64encode(mp3_bytes).decode(),
                    "format": "mp3",
                },
            },
        ]
        response = self.complete(
            model=settings.TRANSCRIBE_MODEL,
            messages=[{"role": "user", "content": content}],
        )
        return response["choices"][0]["message"]["content"].strip()

    def complete(self, model: str, messages: list[dict]) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": messages,
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            return response.json()