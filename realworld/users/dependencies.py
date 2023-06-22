import uuid
from http import HTTPStatus

import jwt
from fastapi import Header, HTTPException

from realworld.config import JWT_ALG, JWT_SECRET
from realworld.database.core import DbSession
from realworld.users.service import get, is_unique

from .schema import AuthUser, NewUser, User, UserBody


async def unique_user(db: DbSession, body: UserBody[NewUser]) -> UserBody[NewUser]:
    if not await is_unique(db, email=body.user.email, username=body.user.username):
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail={"user": ["user with this email or username already exists"]},
        )

    return body


async def get_current_user(db: DbSession, authorization: str = Header(...)) -> AuthUser:
    authorization_exception = HTTPException(
        status_code=HTTPStatus.UNAUTHORIZED, detail="could not validate credentials"
    )
    try:
        token_name, token = authorization.split(" ")
        if token_name.lower() != "token":
            raise authorization_exception

        payload = jwt.decode(
            token,
            JWT_SECRET.get_secret_value(),
            algorithms=[JWT_ALG],
        )

        user_id = uuid.UUID(payload.get("sub"))
        if not user_id:
            raise authorization_exception

        if not (user := await get(db, id=user_id)):
            raise authorization_exception

        return AuthUser(**User.from_orm(user).dict(), token=token, id=user_id)

    except Exception:
        raise authorization_exception
