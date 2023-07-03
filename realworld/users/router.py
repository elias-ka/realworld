from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from realworld.database.core import DbSession
from realworld.users import service
from realworld.users.dependencies import get_current_user
from realworld.users.model import RealWorldUser

from .schema import (
    AuthUser,
    LoginUser,
    NewUser,
    UpdateUser,
    User,
    UserBody,
)

router = APIRouter()


# https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints#registration
@router.post("/users", status_code=HTTPStatus.CREATED, response_model=UserBody[AuthUser])
async def create_user(
    db: DbSession,
    body: UserBody[NewUser],
) -> UserBody[AuthUser]:
    try:
        user = await service.create_user(db, user_in=body.user)
    except IntegrityError:
        raise HTTPException(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            detail={"user": ["a user with this email or username already exists"]},
        ) from None

    authenticated_user = AuthUser(**User.from_orm(user).dict(), token=user.gen_jwt())
    return UserBody(user=authenticated_user)


# https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints#authentication
@router.post(
    "/users/login",
    status_code=HTTPStatus.OK,
    response_model=UserBody[AuthUser],
)
async def log_in_user(db: DbSession, body: UserBody[LoginUser]) -> UserBody[AuthUser]:
    user = await RealWorldUser.by_email(db, body.user.email)

    if user is None or not user.password_matches(body.user.password):
        raise HTTPException(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            detail={"user": ["invalid email or password"]},
        )

    authenticated_user = AuthUser(**User.from_orm(user).dict(), token=user.gen_jwt())
    return UserBody(user=authenticated_user)


# https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints#get-current-user
@router.get("/user", status_code=HTTPStatus.OK, response_model=UserBody[AuthUser])
async def current_user(
    current_user: AuthUser = Depends(get_current_user),
) -> UserBody[AuthUser]:
    return UserBody(user=current_user)


# https://realworld-docs.netlify.app/docs/specs/backend-specs/endpoints#update-user
@router.put(
    "/user",
    status_code=HTTPStatus.OK,
    response_model=UserBody[AuthUser],
)
async def update_user(
    db: DbSession,
    body: UserBody[UpdateUser],
    logged_in_user: AuthUser = Depends(get_current_user),
) -> UserBody[AuthUser]:
    # All fields being None essentially means these routes are the same
    if all(val is None for val in body.user.dict().values()):
        return await current_user()

    if body.user.email is not None and body.user.email != logged_in_user.email:
        if await RealWorldUser.by_email(db, body.user.email) is not None:
            raise HTTPException(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                detail={"email": ["user with this email already exists"]},
            )

    if body.user.username is not None and body.user.username != logged_in_user.username:
        if await RealWorldUser.by_username(db, body.user.username) is not None:
            raise HTTPException(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                detail={"username": ["user with this username already exists"]},
            )

    user = await service.update_user(db, user=logged_in_user, user_in=body.user)

    return UserBody(
        user=AuthUser(
            **User.from_orm(user).dict(),
            token=user.gen_jwt(),
        )
    )
