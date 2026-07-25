from llm.prompts import SYSTEM_PROMPT


def build_messages(
    user_text: str | None = None,
    case_summary: str | None = None,
    history: list[dict] | None = None,
    image_urls: list[str] | None = None,
    extra_context: str | None = None,
) -> list[dict]:
    system_content = SYSTEM_PROMPT
    if extra_context:
        system_content = f"{SYSTEM_PROMPT}\n\n{extra_context}"

    messages: list[dict] = [
        {"role": "system", "content": system_content},
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

    if image_urls:
        content_parts = []

        if user_text:
            content_parts.append(
                {
                    "type": "text",
                    "text": user_text,
                }
            )
        else:
            content_parts.append(
                {
                    "type": "text",
                    "text": "Проанализируйте фото птицы и подскажите, на что обратить внимание.",
                }
            )

        for url in image_urls:
            content_parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": url},
                }
            )

        messages.append(
            {
                "role": "user",
                "content": content_parts,
            }
        )
    else:
        messages.append(
            {
                "role": "user",
                "content": user_text or "",
            }
        )

    return messages