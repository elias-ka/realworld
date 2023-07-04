from http import HTTPStatus

from fastapi import APIRouter, Depends

from realworld.database.core import DbSession
from realworld.profiles import service
from realworld.profiles.exceptions import ProfileNotFoundError
from realworld.profiles.schema import Profile, ProfileBody
from realworld.users.dependencies import get_current_user, maybe_get_current_user
from realworld.users.schema import AuthUser

router = APIRouter()


# https://www.realworld.how/docs/specs/backend-specs/endpoints#get-profile
@router.get("/profiles/{username}", status_code=HTTPStatus.OK, response_model=ProfileBody[Profile])
async def get_user_profile(
    db: DbSession, username: str, maybe_current_user: AuthUser | None = Depends(maybe_get_current_user)
) -> ProfileBody[Profile]:
    profile = await service.get_profile(db, identifier=username, current_user=maybe_current_user)
    if profile is None:
        raise ProfileNotFoundError()

    return ProfileBody(profile=profile)


# https://www.realworld.how/docs/specs/backend-specs/endpoints#follow-user
@router.post("/profiles/{username}/follow", status_code=HTTPStatus.OK, response_model=ProfileBody[Profile])
async def follow_user(
    db: DbSession, username: str, current_user: AuthUser = Depends(get_current_user)
) -> ProfileBody[Profile]:
    profile = await service.follow_user(db, username=username, current_user=current_user)
    if profile is None:
        raise ProfileNotFoundError()

    return ProfileBody(profile=profile)


# https://www.realworld.how/docs/specs/backend-specs/endpoints/#unfollow-user
@router.delete("/profiles/{username}/follow", status_code=HTTPStatus.OK, response_model=ProfileBody[Profile])
async def unfollow_user(
    db: DbSession, username: str, current_user: AuthUser = Depends(get_current_user)
) -> ProfileBody[Profile]:
    profile = await service.unfollow_user(db, username=username, current_user=current_user)
    if profile is None:
        raise ProfileNotFoundError()

    return ProfileBody(profile=profile)
