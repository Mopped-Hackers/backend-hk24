import subprocess
from uuid import uuid4

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from application.initializer import IncludeAPIRouter
from application.main.config import settings


def get_application():
    _app = FastAPI(
        title=settings.API_NAME,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        debug=True,
    )
    _app.include_router(IncludeAPIRouter())
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return _app


app = get_application()


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    error_response = jsonable_encoder(
        {
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": exc.errors(),
            "ptrace": str(uuid4()),
        }
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_response
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> Response:
    error_response = jsonable_encoder(
        {
            "code": exc.status_code,
            "message": exc.detail,
            "ptrace": str(uuid4()),
        }
    )
    return JSONResponse(status_code=exc.status_code, content=error_response)


@app.on_event("shutdown")
async def app_shutdown():
    print("On App Shutdown i will be called.")
