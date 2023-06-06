from pathlib import Path
from typing import List, Union

import yaml
from httpx import Response

from ..model.clash import SS, SSR, Clash, Snell, Socks5, Trojan, Vmess
from ..utils import Download


async def counter(url):
    resp: Response = await Download.client.get(url)
    try:
        return resp.headers.get("subscription-userinfo")
    except KeyError:
        return ""


async def get_sub(url: str) -> List[Union[SS, SSR, Snell, Socks5, Trojan, Vmess]]:
    return Clash.parse_obj(
        yaml.load(await Download.content(url), Loader=yaml.FullLoader)
    ).proxies


async def get_file(file: str) -> List[Union[SS, SSR, Snell, Socks5, Trojan, Vmess]]:
    return Clash.parse_obj(
        yaml.load(Path(file).read_bytes(), Loader=yaml.FullLoader)
    ).proxies
