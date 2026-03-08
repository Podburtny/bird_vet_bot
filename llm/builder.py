from llm.prompts import SYSTEM_PROMPT


def build_messages(
    user_text: str,
    case_summary: str | None = None,
    history: list[dict] | None = None,
) -> list[dict]:
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    if case_summary:
        messages.append(
            {
                "role": "user",
                "content": f"=== CASE SUMMARY ===\n{case_summary}",
            }
        )
        messages.append(
            {
                "role": "assistant",
                "content": "Понял, продолжаем.",
            }
        )

    if history:
        for item in history:
            role = item.get("role", "user")
            content = item.get("content") or ""
            if not content:
                continue
            messages.append(
                {
                    "role": role,
                    "content": content,
                }
            )

    messages.append(
        {
            "role": "user",
            "content": user_text,
        }
    )

    return messages