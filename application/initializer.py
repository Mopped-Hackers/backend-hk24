import pandas as pd
import os
from application.main.config import settings


class LoggerInstance(object):
    def __new__(cls):
        from application.main.utility.logger.custom_logging import LogHandler

        return LogHandler()


class IncludeAPIRouter(object):
    def __new__(cls):
        from fastapi.routing import APIRouter

        router = APIRouter()

        # route 1 -> /
        # ------------------------
        from application.main.routers.default import router as default

        router.include_router(default, prefix="", tags=["default route"])

        # route 2 -> /ai
        # ------------------------
        from application.main.routers.ai import router as ai

        router.include_router(ai, prefix="/ai", tags=["ai route"])

        return router


# instance creation
logger_instance = LoggerInstance()
