import logging
import uuid

import sqlalchemy
from slugify import slugify
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.dialects.postgresql import insert as psql_insert

from realworld.articles.model import ArticleComment, ArticleFavorite, RealWorldArticle
from realworld.articles.schema import (
    Article,
    ArticleCreate,
    ArticleUpdate,
    Comment,
    ListArticlesQuery,
)
from realworld.database.core import DbSession
from realworld.profiles import service as profile_service
from realworld.profiles.model import Follow
from realworld.profiles.schema import Profile
from realworld.users.model import RealWorldUser
from realworld.users.schema import AuthUser, User

logger = logging.getLogger(__name__)


async def create_article(db: DbSession, *, article_in: ArticleCreate, user: AuthUser) -> RealWorldArticle:
    article = RealWorldArticle(user_id=user.user_id, slug=slugify(article_in.title), **article_in.dict())
    db.add(article)
    await db.commit()
    await db.refresh(article)
    return article


async def is_article_favorited_by_user(db: DbSession, *, article_id: uuid.UUID, user: AuthUser) -> bool:
    article = await db.scalar(
        select(RealWorldArticle).where(RealWorldArticle.id == article_id).where(ArticleFavorite.user_id == user.user_id)
    )
    return article is not None


async def get_article_favorites_count(db: DbSession, *, article_id: uuid.UUID) -> int:
    count = await db.scalar(
        select(func.count(ArticleFavorite.article_id)).where(ArticleFavorite.article_id == article_id)
    )
    return count or 0


async def update_article(
    db: DbSession, *, slug: str, article_in: ArticleUpdate, user: AuthUser
) -> RealWorldArticle | None:
    article = await db.scalar(
        update(RealWorldArticle)
        .where(RealWorldArticle.slug == slug)
        .where(RealWorldArticle.user_id == user.user_id)
        .values(**article_in.dict(exclude_unset=True))
        .returning(RealWorldArticle)
    )

    await db.commit()
    await db.refresh(article)
    return article or None


async def delete_article(db: DbSession, *, slug: str, user: AuthUser) -> None:
    await db.execute(
        delete(RealWorldArticle).where(RealWorldArticle.slug == slug).where(RealWorldArticle.user_id == user.user_id)
    )
    await db.commit()


async def build_filter_query(
    db: DbSession,
    *,
    stmt: sqlalchemy.sql.Select,
    params: ListArticlesQuery,
) -> sqlalchemy.sql.Select:
    # Filter articles by tag
    if params.tag is not None:
        query = stmt.where(RealWorldArticle.tag_list.contains([params.tag]))

    # Filter articles by author
    if params.author is not None:
        author = await RealWorldUser.by_username(db, params.author)
        if author is not None:
            query = stmt.where(RealWorldArticle.user_id == author.id)

    # Filter articles favorited by some user
    if params.favorited_by is not None:
        user = await RealWorldUser.by_username(db, params.favorited_by)
        if user is not None:
            query = stmt.join(ArticleFavorite, ArticleFavorite.article_id == RealWorldArticle.id).where(
                ArticleFavorite.user_id == user.id
            )

    # Get the author of each article
    query = stmt.join(RealWorldUser, RealWorldUser.id == RealWorldArticle.user_id)
    return query


async def get_articles(db: DbSession, params: ListArticlesQuery, current_user: AuthUser | None) -> list[Article] | None:
    stmt = (
        select(RealWorldArticle, RealWorldUser)
        .order_by(RealWorldArticle.created_at.desc())
        .offset(min(params.offset, 100))
        .limit(min(params.limit, 100))
    )

    query = await build_filter_query(db, stmt=stmt, params=params)

    results = await db.execute(query)
    return [
        Article(
            **article.dict(),
            favorited=current_user is not None
            and await is_article_favorited_by_user(db, article_id=article.id, user=current_user),
            favorites_count=await get_article_favorites_count(db, article_id=article.id),
            author=Profile(
                **author.dict(),
                following=current_user is not None
                and await profile_service.is_following(db, username=author.username, current_user=current_user),
            ),
        )
        for article, author in results.tuples()
    ]


async def get_feed_articles(db: DbSession, params: ListArticlesQuery, current_user: AuthUser) -> list[Article] | None:
    stmt = (
        select(RealWorldArticle, RealWorldUser)
        .where(Follow.following_user_id == current_user.user_id)
        .where(Follow.followed_user_id == RealWorldArticle.user_id)
        .order_by(RealWorldArticle.created_at.desc())
        .offset(min(params.offset, 100))
        .limit(min(params.limit, 100))
    )

    query = await build_filter_query(db, stmt=stmt, params=params)

    results = await db.execute(query)
    return [
        Article(
            **article.dict(),
            favorited=current_user is not None
            and await is_article_favorited_by_user(db, article_id=article.id, user=current_user),
            favorites_count=await get_article_favorites_count(db, article_id=article.id),
            author=Profile(
                **author.dict(),
                following=current_user is not None
                and await profile_service.is_following(db, username=author.username, current_user=current_user),
            ),
        )
        for article, author in results.tuples()
    ]


async def add_artcicle_comment(db: DbSession, *, slug: str, body: str, current_user: AuthUser) -> ArticleComment | None:
    if (article := await RealWorldArticle.by_slug(db, slug)) is None:
        return None

    comment = await db.scalar(
        insert(ArticleComment)
        .values(
            article_id=article.id,
            user_id=current_user.user_id,
            body=body,
        )
        .returning(ArticleComment)
    )
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_comments(db: DbSession, *, slug: str, current_user: AuthUser | None) -> list[Comment]:
    article = await RealWorldArticle.by_slug(db, slug)
    if article is None:
        return []

    results = await db.execute(
        select(ArticleComment, RealWorldUser)
        .join(RealWorldUser, RealWorldUser.id == ArticleComment.user_id)
        .where(ArticleComment.article_id == article.id)
        .order_by(ArticleComment.created_at.desc())
    )
    return [
        Comment(
            **comment.dict(),
            author=Profile.from_user(
                user=User.from_orm(author),
                following=current_user is not None
                and await profile_service.is_following(db, username=author.username, current_user=current_user),
            ),
        )
        for comment, author in results.tuples()
    ]


async def delete_article_comment(db: DbSession, *, slug: str, comment_id: int, current_user: AuthUser) -> bool:
    if (article := await RealWorldArticle.by_slug(db, slug)) is None:
        return False

    await db.execute(
        delete(ArticleComment)
        .where(ArticleComment.article_id == article.id)
        .where(ArticleComment.id == comment_id)
        .where(ArticleComment.user_id == current_user.user_id)
    )

    await db.commit()
    return True


async def favorite_article(db: DbSession, *, slug: str, current_user: AuthUser) -> Article | None:
    if (article := await RealWorldArticle.by_slug(db, slug)) is None:
        return None

    author = await RealWorldUser.by_id(db, article.user_id)
    if author is None:
        return None

    await db.execute(
        psql_insert(ArticleFavorite)
        .values(
            article_id=article.id,
            user_id=current_user.user_id,
        )
        .on_conflict_do_nothing()
    )

    await db.commit()
    return Article(
        **article.dict(),
        favorited=True,
        favorites_count=await get_article_favorites_count(db, article_id=article.id),
        author=Profile.from_user(
            User.from_orm(author),
            following=await profile_service.is_following(db, username=author.username, current_user=current_user),
        ),
    )


async def unfavorite_article(db: DbSession, *, slug: str, current_user: AuthUser) -> Article | None:
    if (article := await RealWorldArticle.by_slug(db, slug)) is None:
        return None

    author = await RealWorldUser.by_id(db, article.user_id)
    if author is None:
        return None

    await db.execute(
        delete(ArticleFavorite)
        .where(ArticleFavorite.article_id == article.id)
        .where(ArticleFavorite.user_id == current_user.user_id)
    )
    await db.commit()
    return Article(
        **article.dict(),
        favorited=False,
        favorites_count=await get_article_favorites_count(db, article_id=article.id),
        author=Profile.from_user(
            User.from_orm(author),
            following=await profile_service.is_following(db, username=author.username, current_user=current_user),
        ),
    )


async def get_tags(db: DbSession) -> list[str]:
    unnested = func.unnest(RealWorldArticle.tag_list)
    tags = await db.scalars(select(unnested).distinct().order_by(unnested))

    if tags is None:
        return []

    return list(tags.all())
