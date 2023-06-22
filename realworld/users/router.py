from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from realworld.database.core import DbSession
from realworld.users import service
from realworld.users.dependencies import get_current_user, unique_user

from .schema import (
    AuthUser,
    LoginUser,
    NewUser,
    UpdateUser,
    User,
    UserBody,
)

router = APIRouter()


@router.post(
    "/users",
    status_code=HTTPStatus.CREATED,
    response_model=UserBody[AuthUser],
)
async def create_user(
    db: DbSession, body: UserBody[NewUser] = Depends(unique_user)
) -> UserBody[AuthUser]:
    user = await service.create(db, user_in=body.user)
    if user is None:
        raise HTTPException(
            HTTPStatus.INTERNAL_SERVER_ERROR, detail={"user": ["could not be created"]}
        )

    authenticated_user = AuthUser(**User.from_orm(user).dict(), token=user.gen_jwt())
    return UserBody(user=authenticated_user)


@router.post(
    "/users/login",
    status_code=HTTPStatus.OK,
    response_model=UserBody[AuthUser],
)
async def user_login(db: DbSession, body: UserBody[LoginUser]) -> UserBody[AuthUser]:
    user = await service.get_by_field(db, field="email", value=body.user.email)

    if user is None or not user.password_matches(body.user.password):
        raise HTTPException(
            HTTPStatus.UNPROCESSABLE_ENTITY,
            detail={"user": ["invalid email or password"]},
        )

    authenticated_user = AuthUser(**User.from_orm(user).dict(), token=user.gen_jwt())
    return UserBody(user=authenticated_user)


@router.get("/user", status_code=HTTPStatus.OK, response_model=UserBody[AuthUser])
async def current_user(
    current_user: AuthUser = Depends(get_current_user),
) -> UserBody[AuthUser]:
    return UserBody(user=current_user)


@router.put(
    "/user",
    status_code=HTTPStatus.OK,
    response_model=UserBody[AuthUser],
)
async def update_user(
    db: DbSession,
    body: UserBody[UpdateUser] = Depends(unique_user),
    authenticated_user: AuthUser = Depends(get_current_user),
) -> UserBody[AuthUser]:
    # All fields being None essentially means these routes are the same
    if all(val is None for val in body.user.dict().values()):
        return await current_user()

    user = await service.update(db, user=authenticated_user, user_in=body.user)
    if user is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail={"user": ["not found"]})

    authenticated_user = AuthUser(
        **User.from_orm(user).dict(),
        token=user.gen_jwt(),
    )

    return UserBody(user=authenticated_user)
