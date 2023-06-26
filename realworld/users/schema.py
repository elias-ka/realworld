from typing import Generic, TypeVar

import bcrypt
from pydantic import UUID4, EmailStr, Field, HttpUrl, validator
from pydantic.generics import GenericModel

from realworld.schemas import RealWorldBaseModel

T = TypeVar("T", bound="RealWorldBaseModel")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# https://realworld-docs.netlify.app/docs/specs/backend-specs/api-response-format/#users-for-authentication
class UserBody(GenericModel, Generic[T]):
    user: T


class User(RealWorldBaseModel):
    email: EmailStr
    username: str
    bio: str | None = None
    image: HttpUrl | None = None

    class Config:
        orm_mode = True


class AuthUser(User):
    id: UUID4 | None = Field(None, exclude=True)
    token: str | None = None


class NewUser(User):
    password: str

    _hash_password = validator("password", allow_reuse=True)(hash_password)


class LoginUser(RealWorldBaseModel):
    email: EmailStr
    password: str


class UpdateUser(RealWorldBaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str | None = None
    bio: str | None = None
    image: HttpUrl | None = None

    _hash_password = validator("password", allow_reuse=True)(hash_password)
