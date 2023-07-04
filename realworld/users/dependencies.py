from http import HTTPStatus
from typing import Annotated

from fastapi import Header

from realworld.database.core import DbSession
from realworld.users.exceptions import CredentialValidationError, MissingAuthorizationHeaderError, UserNotFoundError
from realworld.users.jwt_claims import JwtClaims
from realworld.users.model import RealWorldUser
from realworld.users.schema import AuthUser, User


def _extract_token(authorization: str, required: bool = True) -> str:
    token_name, token = authorization.split()
    if token_name.lower() != "token":
        raise MissingAuthorizationHeaderError()

    return token


async def get_current_user(db: DbSession, authorization: str = Header()) -> AuthUser:
    token = _extract_token(authorization)

    try:
        claims = JwtClaims.from_token(token)
        if not (user := await RealWorldUser.by_id(db, id=claims.user_id)):
            raise UserNotFoundError()

        return AuthUser(**User.from_orm(user).dict(), token=token, user_id=claims.user_id)

    except Exception:
        raise CredentialValidationError() from None


async def maybe_get_current_user(
    db: DbSession, authorization: Annotated[str | None, Header()] = None
) -> AuthUser | None:
    if not authorization:
        return None

    token = _extract_token(authorization, required=False)

    try:
        claims = JwtClaims.from_token(token)
        if not (user := await RealWorldUser.by_id(db, id=claims.user_id)):
            return None

        return AuthUser(**User.from_orm(user).dict(), token=token, user_id=claims.user_id)

    except Exception:
        return None
