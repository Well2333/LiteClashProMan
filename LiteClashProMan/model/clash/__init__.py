from pathlib import Path
from typing import Dict, List, Literal, Optional, Sequence, Union

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
    rule_providers: Optional[Dict[str, RuleProvider]] = Field(alias="rule-providers")
    rules: List[str]

    @classmethod
    def load(cls, file: str) -> "ClashTemplate":
        return cls.parse_obj(
            yaml.load(
                Path(f"data/template/{file}.yaml").read_bytes(), Loader=yaml.FullLoader
            )
        )

    def render(
        self, proxies: List[Union[SS, SSR, Vmess, Socks5, Snell, Trojan]]
    ) -> "Clash":
        if not proxies:
            return Clash.parse_obj(self.dict(exclude_none=True, by_alias=True))
        proxies_name_list = [proxy.name for proxy in proxies]
        proxy_groups = []
        for group in self.proxy_groups:
            if group.proxies == "__proxies_name_list__":
                group.proxies = proxies_name_list
            proxy_groups.append(group)

        self.proxies = proxies
        self.proxy_groups = proxy_groups
        return Clash.parse_obj(self.dict(exclude_none=True, by_alias=True))


class Clash(ClashTemplate):
    proxies: List[Union[SS, SSR, Vmess, Socks5, Snell, Trojan]]
    proxy_groups: List[ProxyGroup] = Field(alias="proxy-groups")

    def save(self, file: str) -> None:
        Path(f"data/profile/{file}.yaml").write_text(
            yaml.dump(
                self.dict(exclude_none=True, by_alias=True, exclude_unset=True),
                sort_keys=False,
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
