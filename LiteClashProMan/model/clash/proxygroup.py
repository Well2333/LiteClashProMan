from typing import Literal, Optional, Union, List

from pydantic import BaseModel, Extra


class ProxyGroupTemplate(BaseModel, extra=Extra.allow):
    name: str
    type: str
    proxies: Union[List[str], Literal["__proxies_name_list__"]]
    url: Optional[str] = None
    interval: Optional[int] = None
    _index: Optional[int] = None


class ProxyGroup(ProxyGroupTemplate):
    proxies: List[str]
