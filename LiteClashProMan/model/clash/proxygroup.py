from typing import Literal, Optional, Union, List

from pydantic import BaseModel, Extra, validator


class ProxyGroupTemplate(BaseModel, extra=Extra.allow):
    name: str
    type: Literal["select", "url-test"]
    proxies: Union[List[str], Literal["__proxies_name_list__"]]
    url: Optional[str]
    interval: Optional[int]
    _index: Optional[int]

    @validator("url", "interval")
    def check_type(cls, v, values):
        if values["type"] == "url-test" and v is None:
            raise ValueError('When type is "url-test", url and interval cannot be None')
        elif values["type"] != "url-test" and v != None:
            raise ValueError(
                'When type is not "url-test", url and interval must be None'
            )
        return v


class ProxyGroup(ProxyGroupTemplate):
    proxies: List[str]