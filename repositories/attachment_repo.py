from sqlalchemy import select
from sqlalchemy.orm import Session

from models.db import Attachment, Message


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

    def get_recent_attachments_for_case(self, case_id, limit: int = 5) -> list[Attachment]:
        stmt = (
            select(Attachment)
            .join(Message, Attachment.message_id == Message.id)
            .where(Message.case_id == case_id)
            .order_by(Message.created_at.desc(), Attachment.position.asc())
            .limit(limit)
        )
        return list(reversed(self.session.execute(stmt).scalars().all()))