from http import HTTPStatus

from realworld.exceptions import ApiError


class ArticleNotFoundError(ApiError):
    def __init__(self) -> None:
        super().__init__(HTTPStatus.NOT_FOUND, detail={"article": ["not found"]})


class AuthorNotFoundError(ApiError):
    def __init__(self) -> None:
        super().__init__(HTTPStatus.NOT_FOUND, detail={"author": ["not found"]})


class ArticleTitleAlreadyExistsError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail={"title": ["an article with this title already exists"]},
        )


class ArticleCouldNotBeUpdatedError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail={"article": ["could not update article"]},
        )


class ArticleDeleteNotPermittedError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            detail={"article": ["delete operation not permitted or the article does not exist"]},
        )


class ArticleCommentNotFoundError(ApiError):
    def __init__(self) -> None:
        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            detail={"comment": ["not found"]},
        )
