import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as psql_insert

from realworld.database.core import DbSession
from realworld.profiles.model import Follow
from realworld.profiles.schema import Profile
from realworld.users.model import RealWorldUser
from realworld.users.schema import AuthUser


async def get_profile(db: DbSession, *, username: str, maybe_current_user: AuthUser | None) -> Profile | None:
    user = await db.scalar(sa.select(RealWorldUser).filter(RealWorldUser.username == username))

    if user is None:
        return None

    following: bool | None = None
    if maybe_current_user is not None:
        following = await db.scalar(
            sa.select(
                sa.exists()
                .where(Follow.followed_user_id == user.id)
                .where(Follow.following_user_id == maybe_current_user.id)
            )
        )

    return Profile(
        username=user.username,
        bio=user.bio,
        image=user.image,
        following=following if following is not None else False,
    )


async def follow_user(db: DbSession, *, username: str, current_user: AuthUser) -> Profile | None:
    user = await db.scalar(sa.select(RealWorldUser).filter(RealWorldUser.username == username))

    if user is None:
        return None

    insert_stmt = (
        psql_insert(Follow)
        .values(
            followed_user_id=user.id,
            following_user_id=current_user.id,
        )
        .on_conflict_do_nothing()
    )

    await db.execute(insert_stmt)

    return await get_profile(db, username=username, maybe_current_user=current_user)


async def unfollow_user(db: DbSession, *, username: str, current_user: AuthUser) -> Profile | None:
    user = await db.scalar(sa.select(RealWorldUser).filter(RealWorldUser.username == username))

    if user is None:
        return None

    await db.execute(
        sa.delete(Follow).where(Follow.followed_user_id == user.id).where(Follow.following_user_id == current_user.id)
    )

    return await get_profile(db, username=username, maybe_current_user=current_user)
