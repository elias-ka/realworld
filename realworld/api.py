from fastapi import APIRouter

from realworld.articles.router import router as articles_router
from realworld.profiles.router import router as profiles_router
from realworld.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(users_router, tags=["user", "users"])
api_router.include_router(profiles_router, tags=["profiles"])
api_router.include_router(articles_router, tags=["articles"])
