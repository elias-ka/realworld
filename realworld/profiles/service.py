import uuid

from sqlalchemy import delete, exists, select
from sqlalchemy.dialects.postgresql import insert as psql_insert

from realworld.database.core import DbSession
from realworld.profiles.model import Follow
from realworld.profiles.schema import Profile
from realworld.users.model import RealWorldUser
from realworld.users.schema import AuthUser


async def get_profile(db: DbSession, *, identifier: uuid.UUID | str, current_user: AuthUser | None) -> Profile | None:
    if isinstance(identifier, str):
        user = await RealWorldUser.by_username(db, identifier)
    else:
        user = await RealWorldUser.by_id(db, identifier)

    if user is None:
        return None

    following: bool | None = None
    if current_user is not None:
        following = await db.scalar(
            select(
                exists()
                .where(Follow.followed_user_id == user.id)
                .where(Follow.following_user_id == current_user.user_id)
            )
        )

    return Profile(
        username=user.username,
        bio=user.bio,
        image=user.image,
        following=following or False,
    )


async def follow_user(db: DbSession, *, username: str, current_user: AuthUser) -> Profile | None:
    if (user := await RealWorldUser.by_username(db, username)) is None:
        return None

    await db.execute(
        psql_insert(Follow)
        .values(
            followed_user_id=user.id,
            following_user_id=current_user.user_id,
        )
        .on_conflict_do_nothing()
    )
    await db.commit()

    return await get_profile(db, identifier=user.id, current_user=current_user)


async def unfollow_user(db: DbSession, *, username: str, current_user: AuthUser) -> Profile | None:
    if (user := await RealWorldUser.by_username(db, username)) is None:
        return None

    await db.execute(
        delete(Follow).where(Follow.followed_user_id == user.id).where(Follow.following_user_id == current_user.user_id)
    )

    return await get_profile(db, identifier=user.id, current_user=current_user)


async def is_following(db: DbSession, *, username: str, current_user: AuthUser) -> bool:
    if (user := await RealWorldUser.by_username(db, username)) is None:
        return False

    following = await db.scalar(
        select(
            exists().where(Follow.followed_user_id == user.id).where(Follow.following_user_id == current_user.user_id)
        )
    )

    return following or False
