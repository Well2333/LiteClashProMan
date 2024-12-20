import asyncio
from asyncio import Semaphore
from datetime import datetime
from typing import Optional

from anyio import Path
from httpx import AsyncClient, Response
from loguru import logger

from .config import config


class Download:
    sem: Semaphore = None # type: ignore

    @classmethod
    async def content(cls, url: str) -> bytes:
        if not cls.sem:
            cls.sem = Semaphore(config.download_thread)

        async with cls.sem:
            for count in range(config.download_retry):
                try:
                    res = await cls._request(url, config.download_proxy)
                    return res.content
                except Exception as e:
                    logger.error(f"[{count+1}] get {url} failed - {type(e)}:{e}")
        logger.error(f"[{count+1}] {url} has reached the maximum retries, stop retries")
        return b""

    @classmethod
    async def _request(
        cls, url: str, proxy: Optional[str] = config.download_proxy
    ) -> Response:
        if proxy:
            logger.debug(f"downloading {url} by proxy {config.download_proxy}")
            client = AsyncClient(proxy=proxy, follow_redirects=True)
        else:
            logger.debug(f"downloading {url}")
            client = AsyncClient(follow_redirects=True)
        try:
            return await client.get(url, timeout=10)
        except Exception as e:
            if proxy:
                return await cls._request(url, proxy=None)
            raise e

    @classmethod
    async def provider(cls, rulesets) -> None:
        async def download_and_write(name: str, url: str):
            path = Path(f"data/provider/{name}.yaml")
            logger.debug(f"downloading ruleset: {name}")
            bfile = await cls.content(url)
            if bfile:
                await path.write_bytes(updatetime + bfile)

        tasks = []
        logger.info("Start downloading rulesets")
        updatetime = f"# update at {datetime.now()}\n".encode()
        for name in rulesets:
            url = rulesets[name]
            tasks.append(asyncio.create_task(download_and_write(name, url)))
        await asyncio.gather(*tasks)
