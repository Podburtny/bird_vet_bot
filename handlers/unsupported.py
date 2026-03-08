from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.video | F.voice | F.document | F.sticker)
async def handle_unsupported(message: Message) -> None:
    await message.answer(
        "Пока поддерживаются только текст и фотографии. "
        "Видео, голосовые, документы и стикеры не поддерживаются."
    )