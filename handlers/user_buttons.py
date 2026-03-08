from aiogram import Router
from aiogram.types import Message

from database import SessionLocal
from services.case_service import CaseService
from ui.keyboards import main_reply_keyboard

router = Router()


@router.message(lambda message: message.text == "🆕 Новый случай")
async def handle_new_case_button(message: Message) -> None:
    with SessionLocal() as session:
        service = CaseService(session)
        case = service.create_new_case(
            telegram_user_id=message.from_user.id,
            first_name=message.from_user.first_name,
        )

    await message.answer(
        f"🆕 Новый случай создан.\nID: {case.id}",
        reply_markup=main_reply_keyboard(),
    )


@router.message(lambda message: message.text == "✅ Закрыть случай")
async def handle_close_case_button(message: Message) -> None:
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