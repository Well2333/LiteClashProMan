from pathlib import Path
from typing import Dict, List, Literal, Optional, Union, Sequence

import yaml
from pydantic import BaseModel, Extra, Field, validator

from .proxy import SS, SSR, Snell, Socks5, Trojan, Vmess
from .proxygroup import ProxyGroup, ProxyGroupTemplate
from .ruleprovider import RuleProvider


class ClashTemplate(BaseModel, extra=Extra.allow):
    proxies: Union[
        List[Union[SS, SSR, Vmess, Socks5, Snell, Trojan]], Literal["__proxies_list__"]
    ]
    proxy_groups: List[ProxyGroupTemplate] = Field(alias="proxy-groups")
    rule_providers: Optional[Dict[str, RuleProvider]] = Field(
        default=None, alias="rule-providers"
    )
    rules: List[str]

    @classmethod
    def load(cls, file: str) -> "ClashTemplate":
        return cls(
            **yaml.load(
                Path(f"data/template/{file}.yaml").read_bytes(), Loader=yaml.FullLoader
            )
        )

    def render(
        self, proxies: List[Union[SS, SSR, Vmess, Socks5, Snell, Trojan]]
    ) -> "Clash":
        if not proxies:
            return Clash(**self.dict(exclude_none=True, by_alias=True))
        proxies_name_list = [proxy.name for proxy in proxies]
        proxy_groups = []
        for group in self.proxy_groups:
            if group.proxies == "__proxies_name_list__":
                group.proxies = proxies_name_list
            if (
                isinstance(group.proxies, Sequence)
                and "__proxies_name_list__" in group.proxies
            ):
                group.proxies.remove("__proxies_name_list__")
                group.proxies += proxies_name_list
            proxy_groups.append(group)

        self.proxies = proxies
        self.proxy_groups = proxy_groups
        return Clash(**self.dict(exclude_none=True, by_alias=True))


class Clash(ClashTemplate):
    proxies: List[Union[SS, SSR, Vmess, Socks5, Snell, Trojan]]
    proxy_groups: List[ProxyGroup] = Field(alias="proxy-groups")
