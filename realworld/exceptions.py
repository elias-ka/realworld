from fastapi import HTTPException


class ApiError(HTTPException):
    pass
