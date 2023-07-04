from http import HTTPStatus

from realworld.exceptions import ApiError


class UserAlreadyExistsError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail={"user": ["a user with this email or username already exists"]},
        )


class UserNotFoundError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"user": ["not found"]},
        )


class EmailAlreadyExistsError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail={"email": ["a user with this email already exists"]},
        )


class UsernameAlreadyExistsError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail={"username": ["a user with this username already exists"]},
        )


class InvalidEmailOrPasswordError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail={"user": ["invalid email or password"]},
        )


class CredentialValidationError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail={"user": ["credentials could not be validated"]},
        )


class MissingAuthorizationHeaderError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail={"header": ["missing authorization header"]},
        )
