import base64
from pathlib import Path

from config import settings


def to_data_uri(content: bytes, mime_type: str = "image/jpeg") -> str:
    return f"data:{mime_type};base64,{base64.b64encode(content).decode()}"


class LocalStorage:
    """Хранит фото на диске под DATA_DIR/photos. Модели отдаём как data URI."""

    def __init__(self) -> None:
        self.root = settings.data_path / "photos"
        self.root.mkdir(parents=True, exist_ok=True)

    def upload_file(self, path: str, content: bytes, content_type: str = "image/jpeg") -> str:
        dest = self.root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)
        return path

    def read_bytes(self, path: str) -> bytes:
        return (self.root / path).read_bytes()

    def data_uri(self, path: str, mime_type: str = "image/jpeg") -> str:
        return to_data_uri(self.read_bytes(path), mime_type)
