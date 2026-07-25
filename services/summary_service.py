import json

from config import settings
from llm.client import OpenRouterClient

FINALIZE_PROMPT = (
    "Завершён разговор владельца птицы с ветконсультантом. "
    "Верни строго JSON без пояснений и без markdown, вида:\n"
    '{"summary": "1-2 предложения: что случилось и что порекомендовали",\n'
    ' "profile": "обновлённый профиль хозяйства: какие птицы, сколько, возраст, '
    'условия содержания, хронические/повторяющиеся темы"}\n'
    "Профиль дополняй новыми фактами, не выкидывая прежние. Пиши по-русски.\n\n"
    "Текущий профиль хозяйства (может быть пуст):\n%PROFILE%\n\n"
    "Разговор:\n%DIALOG%"
)


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

    def finalize(self, history: list[dict], current_profile: str | None) -> dict:
        """Итоговое резюме кейса + обновлённый профиль хозяйства одним запросом.

        Возвращает {"summary": str|None, "profile": str|None}. Один вызов LLM
        вместо двух — чтобы не тормозить закрытие кейса.
        """
        dialog = "\n".join(
            f"{'Владелец' if item.get('role') == 'user' else 'Консультант'}: {item.get('content') or ''}"
            for item in history
            if item.get("content")
        )
        prompt = FINALIZE_PROMPT.replace("%PROFILE%", current_profile or "(пусто)").replace(
            "%DIALOG%", dialog
        )
        response = self.client.complete(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response["choices"][0]["message"]["content"].strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {"summary": None, "profile": None}
        return {
            "summary": (data.get("summary") or "").strip() or None,
            "profile": (data.get("profile") or "").strip() or None,
        }