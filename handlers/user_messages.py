import asyncio
import contextlib
import logging

from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.types import Message

from database import SessionLocal
from services.case_service import CaseService
from services.llm_service import LLMService
from ui.keyboards import main_reply_keyboard

router = Router()
logger = logging.getLogger(__name__)


async def _typing_loop(bot, chat_id: int) -> None:
    while True:
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(4)


async def answer_text(message: Message, text: str) -> None:
    """Общий путь текстового обращения: сохранить, спросить модель, ответить.
    Используется и для обычных сообщений, и для расшифрованных голосовых."""
    reply_to_message_id = message.reply_to_message.message_id if message.reply_to_message else None
    typing_task = None

    try:
        typing_task = asyncio.create_task(_typing_loop(message.bot, message.chat.id))

        with SessionLocal() as session:
            case_service = CaseService(session)

            case, _saved_message = case_service.save_user_message(
                telegram_user_id=message.from_user.id,
                first_name=message.from_user.first_name,
                content=text,
                tg_message_id=message.message_id,
                reply_to_tg_message_id=reply_to_message_id,
                message_type="text",
            )

            history = case_service.get_history_for_case(case.id, limit=20)
            if history and history[-1]["role"] == "user" and history[-1]["content"] == text:
                history = history[:-1]

            image_urls = case_service.get_recent_image_urls_for_case(case.id, limit=5)
            extra_context = case_service.get_system_context(message.from_user.id)

            llm_service = LLMService()
            assistant_reply = await asyncio.to_thread(
                llm_service.chat,
                text,
                case.summary,
                history,
                image_urls if image_urls else None,
                extra_context,
            )

            case_service.save_assistant_message(
                case_id=case.id,
                content=assistant_reply,
                model_name=llm_service.primary_model,
            )

            case_service.maybe_update_summary(case.id)

        typing_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await typing_task

        await message.answer(
            assistant_reply,
            reply_markup=main_reply_keyboard(),
        )

    except Exception as exc:
        if typing_task:
            typing_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await typing_task

        logger.exception("Failed to process text message: %s", exc)
        await message.answer(
            "⚠️ Не удалось обработать запрос. Попробуйте ещё раз.",
            reply_markup=main_reply_keyboard(),
        )


@router.message()
async def handle_text_message(message: Message) -> None:
    if not message.text:
        return
    await answer_text(message, message.text)