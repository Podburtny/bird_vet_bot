import asyncio
import logging

from aiogram import F, Router
from aiogram.types import Message

from handlers.user_messages import answer_text
from llm.client import OpenRouterClient

router = Router()
logger = logging.getLogger(__name__)


async def _ogg_to_mp3(ogg: bytes) -> bytes:
    """Конвертирует голосовое Telegram (ogg/opus) в mp3 через ffmpeg."""
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-i", "pipe:0", "-f", "mp3", "pipe:1",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    out, _ = await proc.communicate(ogg)
    if proc.returncode != 0 or not out:
        raise RuntimeError("ffmpeg не смог сконвертировать аудио")
    return out


@router.message(F.voice)
async def handle_voice_message(message: Message) -> None:
    try:
        tg_file = await message.bot.get_file(message.voice.file_id)
        buf = await message.bot.download_file(tg_file.file_path)
        mp3 = await _ogg_to_mp3(buf.read())
        transcript = await asyncio.to_thread(OpenRouterClient().transcribe, mp3)
    except Exception as exc:
        logger.exception("Failed to transcribe voice message: %s", exc)
        await message.answer(
            "⚠️ Не смог разобрать голосовое. Попробуйте ещё раз или напишите текстом."
        )
        return

    if not transcript:
        await message.answer("Не расслышал вопрос — повторите, пожалуйста, или напишите текстом.")
        return

    await message.answer(f"🎤 Распознал: {transcript}")
    await answer_text(message, transcript)
