import base64
import json
from datetime import datetime
from typing import List, Optional, Union

from pytz import timezone

from ..model.clash import SS, Vmess
from ..utils import Download
from .base64 import ss, vmess


async def counter(url, tz: Optional[str] = None):
    info = json.loads(await Download.content(url))
    download_ = info["bw_counter_b"]
    total = info["monthly_bw_limit_b"]
    timenow = datetime.now()
    if timenow.month == 12:
        month = 1
        year = timenow.year + 1
    else:
        month = timenow.month + 1
        year = timenow.year
    expire = int(
        datetime(
            year=year,
            month=month,
            day=info["bw_reset_day_of_month"],
            tzinfo=timezone(tz) if tz else None,
        ).timestamp()
    )

    return f"upload=0; download={download_}; total={total}; expire={expire}"


async def get(url: str) -> List[Union[SS, Vmess]]:
    bsubs = await Download.content(url)
    subs = base64.decodebytes(bsubs).decode().split("\n")
    proxies = []
    for sub in subs:
        if sub.startswith("ss://"):
            proxies.append(ss(sub))
        elif sub.startswith("vmess://"):
            proxies.append(vmess(sub))
    return proxies
