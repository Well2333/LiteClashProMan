from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starlette.responses import PlainTextResponse

from ..config import config
from ..subscribe import counter, update_provider, generate_profile


app = FastAPI()

# provider download
if config.replace_template_provider:
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
