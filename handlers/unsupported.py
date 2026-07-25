from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.video | F.document | F.sticker)
async def handle_unsupported(message: Message) -> None:
    await message.answer(
        "Пока поддерживаются текст, фотографии и голосовые сообщения. "
        "Видео, документы и стикеры не поддерживаются."
    )