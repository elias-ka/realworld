from typing import Generic, TypeVar

from pydantic.generics import GenericModel

from realworld.schemas import RealWorldBaseModel

T = TypeVar("T", bound="RealWorldBaseModel")


# https://realworld-docs.netlify.app/docs/specs/backend-specs/api-response-format/#profile
class ProfileBody(GenericModel, Generic[T]):
    profile: T


class Profile(RealWorldBaseModel):
    username: str
    bio: str
    image: str | None = None
    following: bool
