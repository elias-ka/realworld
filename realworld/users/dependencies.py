from http import HTTPStatus
from typing import Annotated

from fastapi import Header, HTTPException

from realworld.database.core import DbSession
from realworld.users.jwt_claims import JwtClaims
from realworld.users.model import RealWorldUser
from realworld.users.schema import AuthUser, User

authorization_exception = HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="could not validate credentials")
missing_authorization_exception = HTTPException(
    status_code=HTTPStatus.UNAUTHORIZED, detail="missing authorization header"
)


async def get_current_user(db: DbSession, authorization: str = Header()) -> AuthUser:
    token_name, token = authorization.split()
    if token_name.lower() != "token":
        raise authorization_exception

    try:
        claims = JwtClaims.from_token(token)
        if not (user := await RealWorldUser.by_id(db, id=claims.user_id)):
            raise authorization_exception

        return AuthUser(**User.from_orm(user).dict(), token=token, user_id=claims.user_id)

    except Exception:
        raise authorization_exception


async def maybe_get_current_user(
    db: DbSession, authorization: Annotated[str | None, Header()] = None
) -> AuthUser | None:
    if not authorization:
        return None

    token_name, token = authorization.split()
    if token_name.lower() != "token":
        return None

    try:
        claims = JwtClaims.from_token(token)
        if not (user := await RealWorldUser.by_id(db, id=claims.user_id)):
            return None

        return AuthUser(**User.from_orm(user).dict(), token=token, user_id=claims.user_id)

    except Exception:
        return None
