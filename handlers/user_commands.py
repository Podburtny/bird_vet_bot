from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database import SessionLocal
from services.case_service import CaseService
from ui.keyboards import main_reply_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Здравствуйте 👋\n"
        "Я бот-консультант по домашней птице.\n"
        "Пришлите описание проблемы или фото.",
        reply_markup=main_reply_keyboard(),
    )


@router.message(Command("newcase"))
async def cmd_newcase(message: Message) -> None:
    with SessionLocal() as session:
        service = CaseService(session)
        service.create_new_case(
            telegram_user_id=message.from_user.id,
            first_name=message.from_user.first_name,
        )

    await message.answer(
        "🆕 Начинаем новый вопрос. Опишите, что случилось, или пришлите фото.",
        reply_markup=main_reply_keyboard(),
    )


@router.message(Command("closecase"))
async def cmd_closecase(message: Message) -> None:
    with SessionLocal() as session:
        service = CaseService(session)
        case = service.close_current_case(message.from_user.id)

    if case is None:
        await message.answer(
            "Сейчас нет открытого случая.",
            reply_markup=main_reply_keyboard(),
        )
        return

    await message.answer(
        "✅ Текущий случай закрыт.",
        reply_markup=main_reply_keyboard(),
    )