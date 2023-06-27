import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starlette.responses import FileResponse

from .config import config
from .log import LOGGING_CONFIG
from .subscribe import counter, update

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
async def profile(path: str):
    path = path.rsplit(".", 1)[0] + ".yaml"
    logger.info(f"A request to download profile {path} was received")
    if path[:-5] not in config.profiles.keys():
        raise HTTPException(404, f"Profile {path} not found")
    resp = FileResponse(
        path=f"data/profile/{path}",
    )
    counter_info = await counter(path[:-5])
    if counter_info:
        resp.headers["subscription-userinfo"] = counter_info
    for h in config.headers:
        resp.headers[h] = config.headers[h]
    return resp


# manual update trigger
@app.get(f"/{config.urlprefix}/update")
async def _():
    logger.info("Update is triggered manually")
    error = await update()
    return str(error) or "update complete"

# test sentry debug
@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0

@app.on_event("startup")
async def startup_event():
    error = await update()
    if error:
        raise error
    logger.info(
        f"Starting up scheduler from crontab {config.update_cron} at timezone {config.update_tz}"
    )
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        update, CronTrigger.from_crontab(config.update_cron, config.update_tz)
    )
    scheduler.start()
    logger.info(
        f"Application startup complete, listening requests from {config.domian}/{config.urlprefix}/"
    )


def main():
    uvicorn.run(app, host=config.host, port=config.port, log_config=LOGGING_CONFIG)
