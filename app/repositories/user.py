from datetime import datetime
from typing import Optional, List
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload

from app.models.user import User
from app.models.profile import Profile


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, password: str, role: str = "user") -> User:
        """Create a new user."""
        user = User(
            email=email,
            password=password,
            role=role
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
        