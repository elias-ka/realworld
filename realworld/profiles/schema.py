from typing import Generic, TypeVar

from pydantic.generics import GenericModel

from realworld.schemas import RealWorldBaseModel
from realworld.users.schema import User

T = TypeVar("T", bound="RealWorldBaseModel")


# https://realworld-docs.netlify.app/docs/specs/backend-specs/api-response-format/#profile
class ProfileBody(GenericModel, Generic[T]):
    profile: T


class Profile(RealWorldBaseModel):
    username: str
    bio: str
    image: str | None = None
    following: bool

    @staticmethod
    def from_user(user: User, following: bool = False) -> "Profile":
        return Profile(
            username=user.username,
            bio=user.bio or "",
            image=user.image,
            following=following,
        )
