import logging

from aiogram import Router
from aiogram.types import Message

from database import SessionLocal
from services.case_service import CaseService
from services.llm_service import LLMService

router = Router()
logger = logging.getLogger(__name__)


@router.message()
async def handle_text_message(message: Message) -> None:
    if not message.text:
        return

    reply_to_message_id = message.reply_to_message.message_id if message.reply_to_message else None

    try:
        with SessionLocal() as session:
            case_service = CaseService(session)

            case, _saved_message = case_service.save_user_message(
                telegram_user_id=message.from_user.id,
                first_name=message.from_user.first_name,
                content=message.text,
                tg_message_id=message.message_id,
                reply_to_tg_message_id=reply_to_message_id,
                message_type="text",
            )

            history = case_service.get_history_for_case(case.id, limit=20)

            if history and history[-1]["role"] == "user" and history[-1]["content"] == message.text:
                history = history[:-1]

            llm_service = LLMService()
            assistant_reply = llm_service.chat(
                user_text=message.text,
                case_summary=case.summary,
                history=history,
            )

            case_service.save_assistant_message(
                case_id=case.id,
                content=assistant_reply,
                model_name=llm_service.primary_model,
            )

        await message.answer(assistant_reply)

    except Exception as exc:
        logger.exception("Failed to process text message: %s", exc)
        await message.answer("Не удалось обработать запрос. Попробуйте ещё раз.")