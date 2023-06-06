from pydantic import BaseModel, Extra


class RuleProvider(BaseModel, extra=Extra.allow):
    type: str
    behavior: str
    url: str
    path: str
    interval: int