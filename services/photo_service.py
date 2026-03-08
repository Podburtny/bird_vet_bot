from uuid import uuid4

from aiogram import Bot

from storage.supabase_storage import SupabaseStorage


class PhotoService:
    def __init__(self) -> None:
        self.storage = SupabaseStorage()

    async def store_telegram_photo(
        self,
        bot: Bot,
        telegram_file_id: str,
        user_id: int,
        case_id,
    ) -> dict:
        telegram_file = await bot.get_file(telegram_file_id)
        file_bytes = await bot.download_file(telegram_file.file_path)
        content = file_bytes.read()

        storage_path = f"{user_id}/{case_id}/{uuid4()}.jpg"
        self.storage.upload_file(
            path=storage_path,
            content=content,
            content_type="image/jpeg",
        )

        signed_url = self.storage.create_signed_url(storage_path)

        return {
            "storage_path": storage_path,
            "signed_url": signed_url,
            "file_size": len(content),
            "mime_type": "image/jpeg",
            "telegram_file_id": telegram_file_id,
        }