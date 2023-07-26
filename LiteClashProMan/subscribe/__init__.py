from pathlib import Path
from typing import List, Union, Dict
import time

import yaml
from loguru import logger

from ..config import config
from ..model.clash import SS, SSR, ClashTemplate, Snell, Socks5, Trojan, Vmess
from ..utils import Download
from . import clash, jms

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version


_subs_caches: Dict[str, Dict] = {}


async def _subs(
    subs: List[str],
) -> List[Union[SS, SSR, Vmess, Socks5, Snell, Trojan]]:
    global _subs_caches
    now = int(time.time())

    proxies = []
    for name in subs:
        sub = config.subscribes[name]
        cache = _subs_caches.get(name)
        if cache and cache["expire_time"] > now:
            logger.debug(f"using cache of subs {name}")
            _proxies = cache["proxies"]
        else:
            if sub.type == "jms":
                _proxies = await jms.get(sub.url)
            if sub.type == "ClashSub":
                _proxies = await clash.get_sub(sub.url)
            if sub.type == "ClashFile":
                _proxies = await clash.get_file(sub.file)
            _subs_caches[name] = {"expire_time": now + 7200, "proxies": _proxies}
        proxies.extend(_proxies)
    return proxies


async def generate_profile(profile: str):
    logger.debug(
        f"Generating profile {profile} from template {config.profiles[profile].template}"
    )

    proxies = await _subs(config.profiles[profile].subs)
    template = ClashTemplate.load(config.profiles[profile].template)
    clash = template.render(proxies)
    if config.replace_template_provider and clash.rule_providers:
        for provider in clash.rule_providers:
            # if provider is exists in local
            # replace it with loacl file
            if Path(f"data/provider/{provider}.yaml").exists():
                clash.rule_providers[provider].url = "/".join(
                    [
                        config.domian,
                        config.urlprefix,
                        "provider",
                        f"{provider}.yaml",
                    ]
                )
    # get clash dict
    if version("pydantic").startswith("2"):  # pydantic v2
        clash_dict = clash.model_dump(
            exclude_none=True, by_alias=True, exclude_unset=True
        )
    else:  # pydantic v1
        clash_dict = clash.dict(exclude_none=True, by_alias=True, exclude_unset=True)

    return yaml.dump(
        clash_dict,
        sort_keys=False,
        allow_unicode=True,
    )


async def update_provider():
    if not config.replace_template_provider:
        return
    logger.info("Start update provider")
    try:
        rulesets = {}
        for profile in config.profiles:
            template = ClashTemplate.load(config.profiles[profile].template)
            if template.rule_providers:
                for provider in template.rule_providers:
                    rulesets[provider] = template.rule_providers[provider].url
        await Download.provider(rulesets)
        logger.success("Provider update complete")

    except Exception as e:
        logger.critical(e)
        return e


async def counter(profile: str):
    if len(config.profiles[profile].subs) != 1:
        logger.warning("Subscribe(s) is not 1, counter function disabled")
        return ""
    sub = config.subscribes[config.profiles[profile].subs[0]]
    if sub.type == "jms" and sub.counter:
        return await jms.counter(sub.counter, sub.subtz)
    elif sub.type == "ClashSub":
        return await clash.counter(sub.url)
    return ""
