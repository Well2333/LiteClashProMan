from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from uvicorn import Config, Server

from .api import app
from .config import config
from .log import LOGGING_CONFIG
from .subscribe import update_provider

if config.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(
        dsn=config.sentry_dsn,
        traces_sample_rate=1.0,
    )


@app.on_event("startup")
async def startup_event():
    error = await update_provider()
    if error:
        raise error
    logger.info(
        f"Starting up scheduler from crontab {config.update_cron} at timezone {config.update_tz}"
    )
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update_provider, CronTrigger.from_crontab(config.update_cron, config.update_tz)
    )
    scheduler.start()
    logger.info(
        f"Application startup complete, listening requests from {config.domian}/{config.urlprefix}/"
    )


def main():
    Server(
        Config(
            app,
            host=config.host,
            port=config.port,
            log_config=LOGGING_CONFIG,
            reload=True,  # Enable "hot-reloading"
            reload_includes=[config.config_file_path],  # Watch 'config.yaml'
        )
    ).run()
