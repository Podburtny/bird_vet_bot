from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Здравствуйте. Я бот-консультант по домашней птице.\n"
        "Пришлите описание проблемы или фото."
    )


@router.message(Command("newcase"))
async def cmd_newcase(message: Message) -> None:
    await message.answer("Новый случай будет создан на следующем этапе.")


@router.message(Command("closecase"))
async def cmd_closecase(message: Message) -> None:
    await message.answer("Закрытие случая будет добавлено на следующем этапе.")