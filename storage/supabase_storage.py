from supabase import create_client

from config import settings


class SupabaseStorage:
    def __init__(self) -> None:
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket = settings.SUPABASE_BUCKET

    def upload_file(self, path: str, content: bytes, content_type: str = "image/jpeg") -> str:
        self.client.storage.from_(self.bucket).upload(
            path=path,
            file=content,
            file_options={"content-type": content_type, "upsert": "false"},
        )
        return path

    def create_signed_url(self, path: str, expires_in: int = 3600) -> str:
        result = self.client.storage.from_(self.bucket).create_signed_url(path, expires_in)
        return result["signedURL"]