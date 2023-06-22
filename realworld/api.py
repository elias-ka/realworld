from fastapi import APIRouter

from realworld.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(users_router, tags=["user", "users"])
