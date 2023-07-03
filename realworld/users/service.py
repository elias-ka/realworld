import sqlalchemy as sa

from realworld.database.core import DbSession

from .model import RealWorldUser
from .schema import AuthUser, NewUser, UpdateUser


async def create_user(db: DbSession, *, user_in: NewUser) -> RealWorldUser:
    user = RealWorldUser(
        password_hash=user_in.password,
        **user_in.dict(exclude={"password"}),
    )
    db.add(user)
    await db.commit()
    return user


async def update_user(db: DbSession, *, user: AuthUser, user_in: UpdateUser) -> RealWorldUser:
    result = await db.execute(
        sa.update(RealWorldUser)
        .where(RealWorldUser.id == user.user_id)
        .values(**user_in.dict(exclude_none=True))
        .returning(RealWorldUser)
    )
    await db.commit()
    return result.scalar_one()
