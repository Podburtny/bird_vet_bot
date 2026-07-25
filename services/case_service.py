from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from config import settings
from repositories.attachment_repo import AttachmentRepository
from repositories.case_repo import CaseRepository
from repositories.message_repo import MessageRepository
from repositories.user_repo import UserRepository
from services.summary_service import SummaryService
from storage.local_storage import LocalStorage


class CaseService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.case_repo = CaseRepository(session)
        self.message_repo = MessageRepository(session)
        self.attachment_repo = AttachmentRepository(session)
        self.summary_service = SummaryService()
        self.storage = LocalStorage()

    def _is_expired(self, case) -> bool:
        last = case.last_active
        if last is None:
            return False
        if last.tzinfo is None:  # SQLite отдаёт naive datetime — считаем его UTC
            last = last.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - last > timedelta(hours=settings.CASE_TIMEOUT_HOURS)

    def _resolve_active_case(self, telegram_user_id: int):
        """Возвращает открытый кейс; если он «протух» по таймауту — закрывает
        его (с резюме и обновлением профиля) и открывает новый."""
        case = self.case_repo.get_open_case_for_user(telegram_user_id)
        if case is not None and self._is_expired(case):
            self._finalize_case(case)
            self.case_repo.close_case(case)
            case = None
        if case is None:
            case = self.case_repo.create_case(user_id=telegram_user_id)
        self.case_repo.touch_case(case)
        return case

    def ensure_user_and_case(
        self,
        telegram_user_id: int,
        first_name: str | None,
        role: str = "user",
    ):
        self.user_repo.create_if_not_exists(
            user_id=telegram_user_id,
            first_name=first_name,
            role=role,
        )

        case = self._resolve_active_case(telegram_user_id)
        self.session.commit()
        return case

    def save_user_message(
        self,
        telegram_user_id: int,
        first_name: str | None,
        content: str | None,
        tg_message_id: int | None,
        reply_to_tg_message_id: int | None = None,
        role: str = "user",
        message_type: str = "text",
    ):
        self.user_repo.create_if_not_exists(
            user_id=telegram_user_id,
            first_name=first_name,
            role=role,
        )

        case = self._resolve_active_case(telegram_user_id)

        message = self.message_repo.create_message(
            case_id=case.id,
            role="user",
            content=content,
            tg_message_id=tg_message_id,
            reply_to_tg_message_id=reply_to_tg_message_id,
            message_type=message_type,
        )

        self.session.commit()
        return case, message

    def save_photo_attachment(
        self,
        message_id,
        storage_path: str,
        telegram_file_id: str | None = None,
        mime_type: str | None = None,
        file_size: int | None = None,
        position: int = 0,
    ):
        attachment = self.attachment_repo.create_attachment(
            message_id=message_id,
            storage_path=storage_path,
            telegram_file_id=telegram_file_id,
            mime_type=mime_type,
            file_size=file_size,
            position=position,
        )
        self.session.commit()
        return attachment

    def save_assistant_message(
        self,
        case_id,
        content: str,
        model_name: str | None = None,
    ):
        message = self.message_repo.create_message(
            case_id=case_id,
            role="assistant",
            content=content,
            message_type="text",
            model_name=model_name,
        )
        self.session.commit()
        return message

    def get_history_for_case(self, case_id, limit: int = 20) -> list[dict]:
        messages = self.message_repo.get_last_messages(case_id=case_id, limit=limit)
        return [
            {
                "role": item.role,
                "content": item.content,
            }
            for item in messages
            if item.content
        ]

    def get_recent_image_urls_for_case(self, case_id, limit: int = 5) -> list[str]:
        attachments = self.attachment_repo.get_recent_attachments_for_case(case_id=case_id, limit=limit)
        urls: list[str] = []

        for attachment in attachments:
            try:
                urls.append(self.storage.data_uri(attachment.storage_path))
            except Exception:
                continue

        return urls

    def _finalize_case(self, case) -> None:
        """При закрытии кейса: итоговое резюме + обновление профиля хозяйства.
        Тихо пропускается, если разговор пустой или LLM недоступен."""
        history = self.get_history_for_case(case.id, limit=40)
        if self.message_repo.count_user_messages(case.id) == 0 or len(history) < 2:
            return
        try:
            profile = self.user_repo.get_profile(case.user_id)
            result = self.summary_service.finalize(history, profile)
        except Exception:
            return
        if result.get("summary"):
            self.case_repo.update_summary(case, result["summary"])
        if result.get("profile"):
            self.user_repo.set_profile(case.user_id, result["profile"])

    def get_system_context(self, telegram_user_id: int) -> str | None:
        """Профиль хозяйства + краткие итоги последних кейсов — для системного
        промпта нового разговора."""
        parts: list[str] = []
        profile = self.user_repo.get_profile(telegram_user_id)
        if profile:
            parts.append("Профиль хозяйства (из прошлых разговоров):\n" + profile)
        summaries = self.case_repo.recent_closed_summaries(telegram_user_id, limit=5)
        if summaries:
            parts.append(
                "Итоги последних обращений (свежие сверху):\n"
                + "\n".join(f"- {s}" for s in summaries)
            )
        return "\n\n".join(parts) if parts else None

    def maybe_update_summary(self, case_id) -> None:
        count = self.message_repo.count_user_messages(case_id)
        if count == 0 or count % 6 != 0:
            return

        case = self.case_repo.get_by_id(case_id)
        if case is None:
            return

        history = self.get_history_for_case(case_id, limit=30)
        summary = self.summary_service.build_summary(history)
        self.case_repo.update_summary(case, summary)
        self.session.commit()

    def create_new_case(
        self,
        telegram_user_id: int,
        first_name: str | None,
        role: str = "user",
    ):
        self.user_repo.create_if_not_exists(
            user_id=telegram_user_id,
            first_name=first_name,
            role=role,
        )

        current_case = self.case_repo.get_open_case_for_user(telegram_user_id)
        if current_case is not None:
            self._finalize_case(current_case)
            self.case_repo.close_case(current_case)

        new_case = self.case_repo.create_case(user_id=telegram_user_id)
        self.session.commit()
        return new_case

    def close_current_case(self, telegram_user_id: int):
        case = self.case_repo.get_open_case_for_user(telegram_user_id)
        if case is None:
            return None

        self._finalize_case(case)
        self.case_repo.close_case(case)
        self.session.commit()
        return case