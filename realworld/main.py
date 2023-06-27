from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from realworld.api import api_router
from realworld.config import LOG_LEVEL
from realworld.logger import configure_logging

load_dotenv()
configure_logging()

app = FastAPI(debug=LOG_LEVEL == "DEBUG")
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
