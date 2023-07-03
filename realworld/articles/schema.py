from datetime import datetime
from typing import Generic, TypeVar

from pydantic import Field
from pydantic.generics import GenericModel

from realworld.profiles.schema import Profile
from realworld.schemas import RealWorldBaseModel

T = TypeVar("T", bound="RealWorldBaseModel")


# https://www.realworld.how/docs/specs/backend-specs/api-response-format/#single-article
class SingleArticleBody(GenericModel, Generic[T]):
    article: T


class Article(RealWorldBaseModel):
    slug: str
    title: str
    description: str
    body: str
    tag_list: list[str]
    created_at: datetime
    updated_at: datetime
    favorited: bool
    favorites_count: int
    author: Profile


# https://www.realworld.how/docs/specs/backend-specs/api-response-format/#multiple-articles
class MultipleArticlesBody(RealWorldBaseModel):
    articles: list[Article]
    articles_count: int


class ArticleCreate(RealWorldBaseModel):
    title: str
    description: str
    body: str
    tag_list: list[str] | None = None


class ArticleUpdate(RealWorldBaseModel):
    title: str | None = None
    description: str | None = None
    body: str | None = None
    # Not sure why tag_list is not in the spec


class ListArticlesQuery(RealWorldBaseModel):
    tag: str | None = None
    author: str | None = None
    favorited_by: str | None = Field(None, alias="favorited")
    limit: int = 20
    offset: int = 0


class Comment(RealWorldBaseModel):
    id: int
    body: str
    author: Profile
    created_at: datetime
    updated_at: datetime


class CommentCreate(RealWorldBaseModel):
    body: str


class SingleCommentBody(GenericModel, Generic[T]):
    comment: T


class MultipleCommentsBody(RealWorldBaseModel):
    comments: list[Comment]


class TagsBody(RealWorldBaseModel):
    tags: list[str]
