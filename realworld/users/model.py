from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from sqlalchemy import DateTime, String, Uuid, func, select
from sqlalchemy.orm import mapped_column

from realworld.config import JWT_EXP_MINUTES
from realworld.database.core import Base, DbSession
from realworld.users.jwt_claims import JwtClaims


class RealWorldUser(Base):
    __tablename__ = "user"

    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    username = mapped_column(String, unique=True, index=True, nullable=False)
    email = mapped_column(String, unique=True, index=True, nullable=False)
    # Assume bio is empty by default since the RealWorld spec doesn't mention it.
    bio = mapped_column(String, nullable=False, default="")
    image = mapped_column(String, nullable=True)
    password_hash = mapped_column(String, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), nullable=True, onupdate=func.now())

    @staticmethod
    async def by_username(db: DbSession, username: str) -> RealWorldUser | None:
        return await db.scalar(select(RealWorldUser).where(RealWorldUser.username == username))

    @staticmethod
    async def by_email(db: DbSession, email: str) -> RealWorldUser | None:
        return await db.scalar(select(RealWorldUser).where(RealWorldUser.email == email))

    @staticmethod
    async def by_id(db: DbSession, id: uuid.UUID) -> RealWorldUser | None:
        return await db.scalar(select(RealWorldUser).where(RealWorldUser.id == id))

    @staticmethod
    async def is_unique(db: DbSession, *, email: str, username: str) -> bool:
        return not await db.scalar(
            select(RealWorldUser).where((RealWorldUser.email == email) | (RealWorldUser.username == username))
        )

    def password_matches(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), str(self.password_hash).encode("utf-8"))

    def gen_jwt(self) -> str:
        now = datetime.now(tz=timezone.utc)
        claims = JwtClaims(
            sub=str(self.id),
            iat=now,
            exp=now + timedelta(minutes=JWT_EXP_MINUTES),
        )
        return claims.encode()
