import asyncio
import contextlib
import logging

from aiogram import Router
from aiogram.enums import ChatAction
from aiogram.types import Message

from database import SessionLocal
from services.album_buffer import AlbumBuffer
from services.case_service import CaseService
from services.llm_service import LLMService
from services.photo_service import PhotoService
from ui.keyboards import main_reply_keyboard

router = Router()
logger = logging.getLogger(__name__)

album_buffer = AlbumBuffer()


async def _typing_loop(bot, chat_id: int) -> None:
    while True:
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(4)


async def _process_photo_batch(messages: list[Message]) -> None:
    if not messages:
        return

    typing_task = None

    try:
        first_message = messages[0]
        bot = first_message.bot
        chat_id = first_message.chat.id

        typing_task = asyncio.create_task(_typing_loop(bot, chat_id))

        caption = ""
        for msg in messages:
            if msg.caption:
                caption = msg.caption
                break

        with SessionLocal() as session:
            case_service = CaseService(session)

            case, saved_message = case_service.save_user_message(
                telegram_user_id=first_message.from_user.id,
                first_name=first_message.from_user.first_name,
                content=caption if caption else "[PHOTO]",
                tg_message_id=first_message.message_id,
                reply_to_tg_message_id=first_message.reply_to_message.message_id if first_message.reply_to_message else None,
                message_type="photo" if not caption else "mixed",
            )

            photo_service = PhotoService()
            current_batch_urls: list[str] = []

            for position, msg in enumerate(messages):
                largest_photo = msg.photo[-1]

                photo_info = await photo_service.store_telegram_photo(
                    bot=bot,
                    telegram_file_id=largest_photo.file_id,
                    user_id=first_message.from_user.id,
                    case_id=case.id,
                )

                case_service.save_photo_attachment(
                    message_id=saved_message.id,
                    storage_path=photo_info["storage_path"],
                    telegram_file_id=photo_info["telegram_file_id"],
                    mime_type=photo_info["mime_type"],
                    file_size=photo_info["file_size"],
                    position=position,
                )

                current_batch_urls.append(photo_info["signed_url"])

            history = case_service.get_history_for_case(case.id, limit=20)
            if history and history[-1]["role"] == "user":
                history = history[:-1]

            previous_case_urls = case_service.get_recent_image_urls_for_case(case.id, limit=5)

            all_image_urls: list[str] = []
            seen = set()

            for url in previous_case_urls + current_batch_urls:
                if url not in seen:
                    seen.add(url)
                    all_image_urls.append(url)

            llm_service = LLMService()
            assistant_reply = await asyncio.to_thread(
                llm_service.chat,
                caption if caption else "Проанализируйте все фото текущего случая и подскажите, что видно и что проверить.",
                case.summary,
                history,
                all_image_urls[:5],
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

        await first_message.answer(
            assistant_reply,
            reply_markup=main_reply_keyboard(),
        )

    except Exception as exc:
        if typing_task:
            typing_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await typing_task

        logger.exception("Failed to process photo batch: %s", exc)

        try:
            await messages[0].answer(
                "⚠️ Не удалось обработать фото. Попробуйте ещё раз.",
                reply_markup=main_reply_keyboard(),
            )
        except Exception:
            pass


@router.message(lambda message: bool(message.photo))
async def handle_photo_message(message: Message) -> None:
    media_group_id = message.media_group_id

    if media_group_id:
        await album_buffer.add(
            media_group_id=str(media_group_id),
            item=message,
            delay=2.5,
            callback=_process_photo_batch,
        )
        return

    await _process_photo_batch([message])