import asyncio
from asyncio import Semaphore
from datetime import datetime
from typing import Optional

from anyio import Path
from httpx import AsyncClient
from loguru import logger

from .config import config


class Download:
    client: Optional[AsyncClient] = None
    sem: Optional[Semaphore] = None

    @classmethod
    def init(cls):
        cls.client = AsyncClient(proxies=config.download_proxy)
        cls.sem = Semaphore(config.download_thread)

    @classmethod
    async def content(cls, url: str) -> bytes:
        if not cls.client or not cls.sem:
            cls.init()

        async with cls.sem:
            for count in range(config.download_retry):
                try:
                    res = await cls.client.get(url, timeout=60)
                    return res.content
                except Exception as e:
                    logger.error(f"[{count+1}] get {url} failed: {e}")
            logger.error(
                f"[{count+1}] {url} has reached the maximum retries, stop retries"
            )
            return b""

    @classmethod
    async def provider(cls, rulesets) -> None:
        async def download_and_write(name: str, url: str):
            path = Path(f"data/provider/{name}.yaml")
            logger.debug(f"downloading ruleset: {name}")
            bfile = await cls.content(url)
            if bfile:
                await path.write_bytes(updatetime + bfile)

        if not cls.client or not cls.sem:
            cls.init()

        tasks = []
        logger.info("Start downloading rulesets")
        updatetime = f"# update at {datetime.now()}\n".encode()
        for name in rulesets:
            url = rulesets[name]
            tasks.append(asyncio.create_task(download_and_write(name, url)))
        await asyncio.gather(*tasks)
