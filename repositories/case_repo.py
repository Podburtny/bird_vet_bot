from datetime import datetime, timedelta, timezone

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

    def get_by_id(self, case_id) -> Case | None:
        stmt = select(Case).where(Case.id == case_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def recent_closed_summaries(self, user_id: int, limit: int = 5) -> list[str]:
        stmt = (
            select(Case.summary)
            .where(
                Case.user_id == user_id,
                Case.status == "closed",
                Case.summary.is_not(None),
            )
            .order_by(Case.closed_at.desc())
            .limit(limit)
        )
        return [row[0] for row in self.session.execute(stmt).all() if row[0]]

    def create_case(self, user_id: int, title: str | None = None) -> Case:
        now = datetime.now(timezone.utc)
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
        now = datetime.now(timezone.utc)
        case.last_active = now
        case.expires_at = now + timedelta(days=3)
        self.session.flush()
        return case

    def update_summary(self, case: Case, summary: str) -> Case:
        case.summary = summary
        self.session.flush()
        return case

    def close_case(self, case: Case) -> Case:
        now = datetime.now(timezone.utc)
        case.status = "closed"
        case.closed_at = now
        self.session.flush()
        return case