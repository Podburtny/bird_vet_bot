from sqlalchemy import select
from sqlalchemy.orm import Session

from models.db import Message


class MessageRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_message(
        self,
        case_id,
        role: str,
        content: str | None,
        tg_message_id: int | None = None,
        reply_to_tg_message_id: int | None = None,
        message_type: str = "text",
        model_name: str | None = None,
    ) -> Message:
        message = Message(
            case_id=case_id,
            role=role,
            content=content,
            tg_message_id=tg_message_id,
            reply_to_tg_message_id=reply_to_tg_message_id,
            message_type=message_type,
            model_name=model_name,
        )
        self.session.add(message)
        self.session.flush()
        return message

    def get_last_messages(self, case_id, limit: int = 20) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.case_id == case_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = self.session.execute(stmt).scalars().all()
        return list(reversed(result))