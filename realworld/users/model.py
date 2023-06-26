import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy import DateTime, String, Uuid, func
from sqlalchemy.orm import mapped_column

from realworld.config import JWT_ALG, JWT_EXP_MINUTES, JWT_SECRET
from realworld.database.core import Base


class RealWorldUser(Base):
    __tablename__ = "user"

    id = mapped_column(Uuid, primary_key=True, index=True, default=uuid.uuid4)
    username = mapped_column(String, unique=True, index=True, nullable=False)
    email = mapped_column(String, unique=True, index=True, nullable=False)
    # Assume bio is empty by default since the RealWorld spec doesn't mention it.
    bio = mapped_column(String, nullable=False, default="")
    image = mapped_column(String, nullable=True)
    password_hash = mapped_column(String, nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at = mapped_column(
        DateTime(timezone=True), nullable=True, onupdate=func.now()
    )

    def password_matches(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"), str(self.password_hash).encode("utf-8")
        )

    def gen_jwt(self) -> str:
        now = datetime.now(tz=timezone.utc)
        payload = {
            "sub": str(self.id),
            "iat": now,
            "exp": now + timedelta(minutes=JWT_EXP_MINUTES),
        }
        return jwt.encode(payload, JWT_SECRET.get_secret_value(), JWT_ALG)
