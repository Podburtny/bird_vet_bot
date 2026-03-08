from sqlalchemy.orm import Session

from models.db import Attachment


class AttachmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_attachment(
        self,
        message_id,
        storage_path: str,
        telegram_file_id: str | None = None,
        mime_type: str | None = None,
        file_size: int | None = None,
        position: int = 0,
    ) -> Attachment:
        attachment = Attachment(
            message_id=message_id,
            storage_path=storage_path,
            telegram_file_id=telegram_file_id,
            mime_type=mime_type,
            file_size=file_size,
            position=position,
        )
        self.session.add(attachment)
        self.session.flush()
        return attachment