from http import HTTPStatus

from realworld.exceptions import ApiError


class ProfileNotFoundError(ApiError):
    def __init__(self) -> None:
        super().__init__(HTTPStatus.NOT_FOUND, detail={"profile": ["not found"]})
