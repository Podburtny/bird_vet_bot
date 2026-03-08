from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message()
async def handle_text_message(message: Message) -> None:
    if not message.text:
        return

    await message.answer(
        "Сообщение получено. Дальше подключим обработку кейсов и LLM."
    )