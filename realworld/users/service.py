import uuid

import sqlalchemy as sa

from realworld.database.core import DbSession

from .model import RealWorldUser
from .schema import AuthUser, NewUser, UpdateUser


async def create(db: DbSession, *, user_in: NewUser) -> RealWorldUser:
    user = RealWorldUser(
        password_hash=user_in.password,
        **user_in.dict(exclude={"password"}),
    )
    db.add(user)
    await db.commit()
    return user


async def get(db: DbSession, *, id: uuid.UUID) -> RealWorldUser | None:
    return await db.get(RealWorldUser, id)


async def get_by_field(
    db: DbSession, *, field: str, value: str
) -> RealWorldUser | None:
    results = await db.execute(
        sa.select(RealWorldUser).where(getattr(RealWorldUser, field) == value)
    )
    await db.commit()
    return results.scalars().first()


async def is_unique(db: DbSession, *, email: str, username: str) -> bool:
    results = await db.execute(
        sa.select(RealWorldUser).where(
            (RealWorldUser.email == email) | (RealWorldUser.username == username)
        )
    )
    await db.commit()
    return not results.scalars().first()


async def update(
    db: DbSession, *, user: AuthUser, user_in: UpdateUser
) -> RealWorldUser | None:
    results = await db.execute(
        sa.update(RealWorldUser)
        .where(RealWorldUser.id == user.id)
        .values(**user_in.dict(exclude_none=True))
        .returning(RealWorldUser)
    )
    await db.commit()
    return results.scalars().first()
