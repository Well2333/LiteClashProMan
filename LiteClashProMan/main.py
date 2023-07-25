from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starlette.responses import PlainTextResponse
from uvicorn import Config, Server

from .config import config
from .log import LOGGING_CONFIG
from .subscribe import counter, update_provider, generate_profile

if config.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(
        dsn=config.sentry_dsn,
        traces_sample_rate=1.0,
    )


app = FastAPI()

# provider download
app.mount(f"/{config.urlprefix}/provider", StaticFiles(directory="data/provider"))


# profile download
@app.get(f"/{config.urlprefix}/profile" + "/{path}")
async def profile(request: Request, path: str, id: str = None):
    path = path.rsplit(".", 1)[0] + ".yaml"

    # check profile is exists
    if not (profile_ := config.profiles.get(path[:-5])):
        raise HTTPException(404, f"Profile {path} not found")

    # check id if ids exists
    if profile_.ids and id not in profile_.ids:
        raise HTTPException(status_code=403, detail="Invalid ID")

    # logging id and ip
    user_ip = request.headers.get("X-Real-IP", request.client.host)
    logger.info(
        f"A request from {id}({user_ip}) to download profile {path} was received"
    )

    resp = PlainTextResponse(
        content=await generate_profile(path[:-5]), headers=config.headers.copy()
    )
    counter_info = await counter(path[:-5])
    if counter_info:
        resp.headers["subscription-userinfo"] = counter_info
    return resp


# manual update trigger
@app.get(f"/{config.urlprefix}/update")
async def _():
    logger.info("Update is triggered manually")
    error = await update_provider()
    return str(error) or "update complete"


# test sentry debug
@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0


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
