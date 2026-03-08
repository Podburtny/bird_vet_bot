from datetime import datetime, timedelta, UTC

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.db import Case


class CaseRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_open_case_for_user(self, user_id: int) -> Case | None:
        stmt = (
            select(Case)
            .where(Case.user_id == user_id, Case.status == "open")
            .order_by(Case.last_active.desc())
            .limit(1)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def create_case(self, user_id: int, title: str | None = None) -> Case:
        now = datetime.now(UTC)
        case = Case(
            user_id=user_id,
            title=title,
            status="open",
            created_at=now,
            last_active=now,
            expires_at=now + timedelta(days=3),
        )
        self.session.add(case)
        self.session.flush()
        return case

    def touch_case(self, case: Case) -> Case:
        now = datetime.now(UTC)
        case.last_active = now
        case.expires_at = now + timedelta(days=3)
        self.session.flush()
        return case

    def close_case(self, case: Case) -> Case:
        now = datetime.now(UTC)
        case.status = "closed"
        case.closed_at = now
        self.session.flush()
        return case