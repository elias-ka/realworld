import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError

from realworld.articles.model import RealWorldArticle
from realworld.database.core import DbSession
from realworld.profiles import service as profile_service
from realworld.profiles.schema import Profile
from realworld.users.dependencies import get_current_user, maybe_get_current_user
from realworld.users.schema import AuthUser

from . import service
from .schema import (
    Article,
    ArticleCreate,
    ArticleUpdate,
    Comment,
    CommentCreate,
    ListArticlesQuery,
    MultipleArticlesBody,
    MultipleCommentsBody,
    SingleArticleBody,
    SingleCommentBody,
    TagsBody,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# https://www.realworld.how/docs/specs/backend-specs/endpoints/#feed-articles
@router.get("/articles/feed", response_model=MultipleArticlesBody)
async def get_feed_articles(
    db: DbSession,
    query: ListArticlesQuery = Depends(),
    current_user: AuthUser = Depends(get_current_user),
) -> MultipleArticlesBody:
    articles = await service.get_feed_articles(db, params=query, current_user=current_user)
    return MultipleArticlesBody(articles=articles or [], articles_count=len(articles or []))


# https://www.realworld.how/docs/specs/backend-specs/endpoints/#create-article
@router.post("/articles", response_model=SingleArticleBody[Article])
async def create_article(
    db: DbSession,
    body: SingleArticleBody[ArticleCreate],
    current_user: AuthUser = Depends(get_current_user),
) -> SingleArticleBody[Article]:
    if body.article.tag_list is not None:
        body.article.tag_list.sort()

    try:
        article = await service.create_article(db, article_in=body.article, user=current_user)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail={"article": "an article with this title already exists"}
        ) from None

    return SingleArticleBody(
        article=Article(
            **article.dict(),
            favorited=False,
            favorites_count=0,
            author=Profile.from_user(current_user),
        )
    )


# https://www.realworld.how/docs/specs/backend-specs/endpoints/#get-article
@router.get("/articles/{slug}", response_model=SingleArticleBody[Article])
async def get_article(
    db: DbSession,
    slug: str,
    current_user: Annotated[AuthUser, Depends(maybe_get_current_user)],
) -> SingleArticleBody[Article]:
    if (article := await RealWorldArticle.by_slug(db, slug)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={"article": "article not found"})

    if (author := await profile_service.get_profile(db, identifier=article.user_id, current_user=current_user)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={"author": "author not found"})

    favorited = (
        await service.is_article_favorited_by_user(db, article_id=article.id, user=current_user)
        if current_user is not None
        else False
    )

    return SingleArticleBody(
        article=Article(
            **article.dict(),
            favorited=favorited,
            favorites_count=await service.get_article_favorites_count(db, article_id=article.id),
            author=author,
        )
    )


# https://www.realworld.how/docs/specs/backend-specs/endpoints/#update-article
@router.put("/articles/{slug}", response_model=SingleArticleBody[Article])
async def update_article(
    db: DbSession,
    slug: str,
    body: SingleArticleBody[ArticleUpdate],
    current_user: AuthUser = Depends(get_current_user),
) -> SingleArticleBody[Article]:
    if (_ := await RealWorldArticle.by_slug(db, slug)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={"article": "article not found"})

    try:
        article = await service.update_article(db, slug=slug, article_in=body.article, user=current_user)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail={"article": "an article with this title already exists"}
        ) from None

    if article is None:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail={"article": "could not update article"}
        )

    return SingleArticleBody(
        article=Article(
            **article.dict(),
            favorited=False,
            favorites_count=await service.get_article_favorites_count(db, article_id=article.id),
            author=Profile.from_user(current_user),
        )
    )


# https://www.realworld.how/docs/specs/backend-specs/endpoints/#delete-article
@router.delete("/articles/{slug}")
async def delete_article(
    db: DbSession,
    slug: str,
    current_user: AuthUser = Depends(get_current_user),
) -> None:
    try:
        await service.delete_article(db, slug=slug, user=current_user)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail={"article": "delete operation not permitted or the article does not exist"},
        ) from None


# https://www.realworld.how/docs/specs/backend-specs/endpoints/#list-articles
@router.get("/articles", response_model=MultipleArticlesBody)
async def list_articles(
    db: DbSession,
    query: ListArticlesQuery = Depends(),
    current_user: AuthUser | None = Depends(maybe_get_current_user),
) -> MultipleArticlesBody:
    articles = await service.get_articles(db, params=query, current_user=current_user)
    return MultipleArticlesBody(articles=articles or [], articles_count=len(articles or []))


# https://www.realworld.how/docs/specs/backend-specs/endpoints/#favorite-article
@router.post("/articles/{slug}/favorite", response_model=SingleArticleBody[Article])
async def favorite_article(
    db: DbSession,
    slug: str,
    current_user: AuthUser = Depends(get_current_user),
) -> SingleArticleBody[Article]:
    article = await service.favorite_article(db, slug=slug, current_user=current_user)
    if article is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={"article": "not found"})

    return SingleArticleBody(article=article)


# https://www.realworld.how/docs/specs/backend-specs/endpoints/#unfavorite-article
@router.delete("/articles/{slug}/favorite", response_model=SingleArticleBody[Article])
async def unfavorite_article(
    db: DbSession,
    slug: str,
    current_user: AuthUser = Depends(get_current_user),
) -> SingleArticleBody[Article]:
    article = await service.unfavorite_article(db, slug=slug, current_user=current_user)
    if article is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={"article": "not found"})

    return SingleArticleBody(article=article)


# https://www.realworld.how/docs/specs/backend-specs/endpoints/#get-tags
@router.get("/tags", response_model=TagsBody)
async def get_tags(db: DbSession) -> TagsBody:
    return TagsBody(tags=await service.get_tags(db))


# https://www.realworld.how/docs/specs/backend-specs/endpoints/#add-comments-to-an-article
@router.post("/articles/{slug}/comments", response_model=SingleCommentBody[Comment])
async def add_article_comment(
    db: DbSession,
    slug: str,
    body: SingleCommentBody[CommentCreate],
    current_user: AuthUser = Depends(get_current_user),
) -> SingleCommentBody[Comment]:
    comment = await service.add_artcicle_comment(db, slug=slug, body=body.comment.body, current_user=current_user)
    if comment is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail={"article": "not found"})

    return SingleCommentBody(comment=Comment(**comment.dict(), author=Profile.from_user(current_user)))


# https://www.realworld.how/docs/specs/backend-specs/endpoints/#delete-comment
@router.delete("/articles/{slug}/comments/{comment_id}")
async def delete_article_comment(
    db: DbSession,
    slug: str,
    comment_id: int,
    current_user: AuthUser = Depends(get_current_user),
) -> None:
    if not await service.delete_article_comment(db, slug=slug, comment_id=comment_id, current_user=current_user):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"comment": "not found"},
        )


# https://www.realworld.how/docs/specs/backend-specs/endpoints/#get-comments-from-an-article
@router.get("/articles/{slug}/comments", response_model=MultipleCommentsBody)
async def get_comments(
    db: DbSession,
    slug: str,
    current_user: AuthUser | None = Depends(maybe_get_current_user),
) -> MultipleCommentsBody:
    comments = await service.get_comments(db, slug=slug, current_user=current_user)
    return MultipleCommentsBody(comments=comments)
