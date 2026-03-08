import asyncio
import contextlib
import logging

from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.types import Message

from database import SessionLocal
from services.case_service import CaseService
from services.llm_service import LLMService
from services.photo_service import PhotoService
from ui.keyboards import main_reply_keyboard

router = Router()
logger = logging.getLogger(__name__)


async def _typing_loop(bot, chat_id: int) -> None:
    while True:
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(4)


@router.message(lambda message: bool(message.photo))
async def handle_photo_message(message: Message) -> None:
    typing_task = None

    try:
        typing_task = asyncio.create_task(_typing_loop(message.bot, message.chat.id))

        largest_photo = message.photo[-1]
        caption = message.caption or ""

        with SessionLocal() as session:
            case_service = CaseService(session)

            case, saved_message = case_service.save_user_message(
                telegram_user_id=message.from_user.id,
                first_name=message.from_user.first_name,
                content=caption if caption else "[PHOTO]",
                tg_message_id=message.message_id,
                reply_to_tg_message_id=message.reply_to_message.message_id if message.reply_to_message else None,
                message_type="photo" if not caption else "mixed",
            )

            photo_service = PhotoService()
            photo_info = await photo_service.store_telegram_photo(
                bot=message.bot,
                telegram_file_id=largest_photo.file_id,
                user_id=message.from_user.id,
                case_id=case.id,
            )

            case_service.save_photo_attachment(
                message_id=saved_message.id,
                storage_path=photo_info["storage_path"],
                telegram_file_id=photo_info["telegram_file_id"],
                mime_type=photo_info["mime_type"],
                file_size=photo_info["file_size"],
                position=0,
            )

            history = case_service.get_history_for_case(case.id, limit=20)

            if history and history[-1]["role"] == "user":
                history = history[:-1]

            llm_service = LLMService()

            assistant_reply = await asyncio.to_thread(
                llm_service.chat,
                caption if caption else "Посмотрите фото птицы и подскажите, что видно и что проверить.",
                case.summary,
                history,
                [photo_info["signed_url"]],
            )

            case_service.save_assistant_message(
                case_id=case.id,
                content=assistant_reply,
                model_name=llm_service.primary_model,
            )

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

        logger.exception("Failed to process photo message: %s", exc)
        await message.answer(
            "⚠️ Не удалось обработать фото. Попробуйте ещё раз.",
            reply_markup=main_reply_keyboard(),
        )