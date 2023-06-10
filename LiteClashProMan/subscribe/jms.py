import base64
import json
from datetime import datetime
from typing import List, Optional, Union

from pytz import timezone

from ..model.clash import SS, Vmess
from ..utils import Download
from .base64 import ss, vmess


async def counter(url, tz: Optional[str] = None):
    tz = timezone(tz) if tz else None
    info = json.loads(await Download.content(url))
    download_ = info["bw_counter_b"]
    total = info["monthly_bw_limit_b"]
    expire_time = datetime.now(tz)

    if expire_time.day >= info["bw_reset_day_of_month"]:
        # If today's date passes reset_day_of_month
        # the next month should be taken
        if expire_time.month == 12:
            year = expire_time.year + 1
            month = expire_time.month = 1
        else:
            year = expire_time.year
            month = expire_time.month + 1
    else:
        year = expire_time.year
        month = expire_time.month

    expire = int(
        datetime(
            year=year,
            month=month,
            day=info["bw_reset_day_of_month"],
            tzinfo=tz,
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
