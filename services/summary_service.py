from config import settings
from llm.client import OpenRouterClient


class SummaryService:
    def __init__(self) -> None:
        self.client = OpenRouterClient()
        self.model = settings.SUMMARY_MODEL

    def build_summary(self, history: list[dict]) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "Сделайте краткую сводку ветеринарного кейса по домашней птице. "
                    "Пишите по-русски. "
                    "Сводка должна быть 3–5 коротких предложений. "
                    "Отразите: симптомы, длительность, что уже обсуждали, что уже советовали, текущее состояние."
                ),
            }
        ]

        for item in history:
            content = item.get("content") or ""
            role = item.get("role", "user")
            if content:
                messages.append({"role": role, "content": content})

        response = self.client.complete(
            model=self.model,
            messages=messages,
        )

        return response["choices"][0]["message"]["content"].strip()