from sqlalchemy.orm import Session

from repositories.case_repo import CaseRepository
from repositories.message_repo import MessageRepository
from repositories.user_repo import UserRepository


class CaseService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.case_repo = CaseRepository(session)
        self.message_repo = MessageRepository(session)

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

        case = self.case_repo.get_open_case_for_user(telegram_user_id)
        if case is None:
            case = self.case_repo.create_case(user_id=telegram_user_id)

        self.case_repo.touch_case(case)
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

        case = self.case_repo.get_open_case_for_user(telegram_user_id)
        if case is None:
            case = self.case_repo.create_case(user_id=telegram_user_id)

        self.case_repo.touch_case(case)

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
            self.case_repo.close_case(current_case)

        new_case = self.case_repo.create_case(user_id=telegram_user_id)
        self.session.commit()
        return new_case

    def close_current_case(self, telegram_user_id: int):
        case = self.case_repo.get_open_case_for_user(telegram_user_id)
        if case is None:
            return None

        self.case_repo.close_case(case)
        self.session.commit()
        return case