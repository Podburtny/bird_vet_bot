from sqlalchemy import select
from sqlalchemy.orm import Session

from models.db import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_if_not_exists(self, user_id: int, first_name: str | None, role: str = "user") -> User:
        user = self.get_by_id(user_id)
        if user:
            return user

        user = User(
            id=user_id,
            first_name=first_name,
            role=role,
        )
        self.session.add(user)
        self.session.flush()
        return user