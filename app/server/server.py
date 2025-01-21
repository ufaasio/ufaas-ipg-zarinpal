from apps.config.routes import router as config_router
from apps.zarinpal.routes import router as zarinpal_router
from fastapi_mongo_base.core import app_factory

from . import config

app = app_factory.create_app(settings=config.Settings(), original_host_middleware=True)
app.include_router(config_router, prefix=f"{config.Settings.base_path}", include_in_schema=False)
app.include_router(zarinpal_router, prefix=f"{config.Settings.base_path}")
