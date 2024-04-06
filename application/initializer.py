class LoggerInstance:
    def __new__(cls) -> object:
        from application.main.utility.logger.custom_logging import LogHandler

        return LogHandler()


class IncludeAPIRouter:
    def __new__(cls) -> object:
        from fastapi.routing import APIRouter

        router = APIRouter()

        # route 1 -> /
        # ------------------------
        from application.main.routers.default import router as default

        router.include_router(default, prefix="", tags=["default route"])

        return router


# instance creation
logger_instance = LoggerInstance()
