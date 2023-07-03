from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Uuid, func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import mapped_column

from realworld.database.core import Base, DbSession


class RealWorldArticle(Base):
    __tablename__ = "article"
    __table_args__ = (Index("ix_article_tags_gin", "tag_list", postgresql_using="gin"),)
    id = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id = mapped_column(Uuid, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    # Slug is the title of the article in lowercase and hyphenated, it must be unique here because
    # it's used to look up an article.
    slug = mapped_column(String, nullable=False, unique=True)
    title = mapped_column(String, nullable=False)
    description = mapped_column(String, nullable=False)
    body = mapped_column(String, nullable=False)
    tag_list = mapped_column(postgresql.ARRAY(String, dimensions=1), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), nullable=False, onupdate=func.now(), server_default=func.now())

    @staticmethod
    async def by_id(db: DbSession, article_id: uuid.UUID) -> RealWorldArticle | None:
        return await db.scalar(select(RealWorldArticle).where(RealWorldArticle.id == article_id))

    @staticmethod
    async def by_slug(db: DbSession, slug: str) -> RealWorldArticle | None:
        return await db.scalar(select(RealWorldArticle).where(RealWorldArticle.slug == slug))


class ArticleFavorite(Base):
    __tablename__ = "article_favorite"
    article_id = mapped_column(
        Uuid,
        ForeignKey("article.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    user_id = mapped_column(Uuid, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())


class ArticleComment(Base):
    __tablename__ = "article_comment"
    # I would just use a UUID here but the RealWorld spec uses an integer.
    # The id should not be used to sort comments, so I'll use created_at instead.
    id = mapped_column(BigInteger, primary_key=True)
    article_id = mapped_column(Uuid, ForeignKey("article.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = mapped_column(Uuid, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    body = mapped_column(String, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    updated_at = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
