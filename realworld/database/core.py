from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from realworld import config

async_engine = create_async_engine(
    config.SQLALCHEMY_DATABASE_URI,
    pool_size=config.DATABASE_ENGINE_POOL_SIZE,
)

sessionmaker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=True,
    expire_on_commit=False,
)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(get_db)]
