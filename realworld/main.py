from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from realworld import config
from realworld.api import api_router
from realworld.logger import configure_logging

load_dotenv()
configure_logging()

app = FastAPI(debug=config.LOG_LEVEL == "DEBUG", openapi_url=None, docs_url=None, redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ALLOWED_ORIGINS if not config.CORS_ORIGIN_ALLOW_ALL else ["*"],
    allow_headers=config.CORS_ALLOW_HEADERS if not config.CORS_ORIGIN_ALLOW_ALL else ["*"],
    allow_methods=config.CORS_ALLOW_METHODS if not config.CORS_ORIGIN_ALLOW_ALL else ["*"],
)
app.include_router(api_router, prefix="/api")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"errors": exc.detail},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
