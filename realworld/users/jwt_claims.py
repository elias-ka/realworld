from __future__ import annotations

import uuid
from datetime import datetime

import jwt
from pydantic import BaseModel

from realworld import config


class JwtClaims(BaseModel):
    sub: str
    iat: datetime
    exp: datetime

    @property
    def user_id(self) -> uuid.UUID:
        try:
            return uuid.UUID(self.sub)
        except ValueError:
            raise ValueError("invalid user id") from None

    def encode(self) -> str:
        return jwt.encode(self.dict(), config.JWT_SECRET.get_secret_value(), config.JWT_ALG)

    @classmethod
    def from_token(cls: type[JwtClaims], token: str) -> JwtClaims:
        try:
            return cls(**jwt.decode(token, config.JWT_SECRET.get_secret_value(), algorithms=[config.JWT_ALG]))
        except jwt.DecodeError:
            raise ValueError("invalid token") from None
