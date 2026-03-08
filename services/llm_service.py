from llm.builder import build_messages
from llm.client import OpenRouterClient


class LLMService:
    def __init__(self) -> None:
        self.client = OpenRouterClient()
        self.primary_model = "google/gemini-2.5-pro"

    def chat(
        self,
        user_text: str | None = None,
        case_summary: str | None = None,
        history: list[dict] | None = None,
        image_urls: list[str] | None = None,
    ) -> str:
        messages = build_messages(
            user_text=user_text,
            case_summary=case_summary,
            history=history,
            image_urls=image_urls,
        )

        response = self.client.complete(
            model=self.primary_model,
            messages=messages,
        )

        return response["choices"][0]["message"]["content"].strip()