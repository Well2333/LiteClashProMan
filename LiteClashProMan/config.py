import json
from pathlib import Path
from typing import Dict, List, Literal, Optional, Union, Set

import yaml
from pydantic import BaseModel, Extra, validator
from pytz import UnknownTimeZoneError, timezone


class Subscribe(BaseModel, extra=Extra.allow):
    type: str
    subtz: str = "Asia/Shanghai"

    @validator("subtz")
    def check_timezone(cls, tz: str):
        try:
            timezone(tz)
        except UnknownTimeZoneError as e:
            raise ValueError(f"Timezone {tz} could not be resolved") from e
        return tz


class JMS(Subscribe):
    """just my socks"""

    type: Literal["jms"] = "jms"
    url: str
    counter: Optional[str]


class ClashSub(Subscribe):
    """Generic clash profile subscription"""

    type: Literal["ClashSub"] = "ClashSub"
    url: str


class ClashFile(Subscribe):
    """Generic clash profile on local disk"""

    type: Literal["ClashFile"] = "ClashFile"
    file: str


class Profile(BaseModel):
    template: str
    subs: List[str] = []
    ids: Set[str] = set()


class Config(BaseModel, extra=Extra.ignore):
    log_level: Literal[
        "TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    ] = "INFO"
    sentry_dsn: Optional[str]

    download_thread: int = 4
    download_retry: int = 3
    download_proxy: Optional[str] = None

    update_cron: str = "35 6 * * *"
    update_tz: str = "Asia/Shanghai"

    domian: str = "http://0.0.0.0:46199"
    host: str = "127.0.0.1"
    port: int = 46199
    urlprefix: str = "/path/to/mess/url"
    headers: Dict[str, str] = {"profile-update-interval": "24"}

    subscribes: Dict[str, Union[JMS, ClashSub, ClashFile]]
    profiles: Dict[str, Profile]

    config_file_path: str

    @validator("port")
    def check_port(cls, p):
        if p > 65535 or p <= 0:
            raise ValueError(f"Port number must be in the range 0 to 65535, not {p}")
        return p

    @validator("update_tz")
    def check_timezone(cls, tz: str):
        try:
            timezone(tz)
        except UnknownTimeZoneError as e:
            raise ValueError(f"Timezone {tz} could not be resolved") from e
        return tz

    @validator("urlprefix", "domian", pre=True)
    def format_urlprefix(cls, v: str):
        return v.strip("/")

    @validator("profiles")
    def validate_profiles(cls, v: Dict[str, Profile], values):
        for profile in v.values():
            # check template
            if not Path(f"data/template/{profile.template}.yaml").exists():
                raise ValueError(f"template {profile.template}.yaml not exists")
            # check subscribes
            for sub in profile.subs:
                if sub not in values["subscribes"].keys():
                    raise ValueError(f"subscribe {sub} not exists")
        return v

    @staticmethod
    def _create_file(file: Path):
        file.write_text(
            Path(__file__)
            .parent.joinpath("static/config.exp.yaml")
            .read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    @staticmethod
    def valueerror_parser(e: ValueError):
        return {
            ".".join([str(x) for x in err["loc"]]): err["msg"]
            for err in json.loads(e.json())
        }

    @classmethod
    def load(cls, file: Path):
        global config
        if not file.exists():
            cls._create_file(file)
            raise FileNotFoundError(
                f"Configuration file not found in {file}, a blank configuration file was created at that location"
            )
        config = cls(
            **yaml.load(file.read_bytes(), Loader=yaml.FullLoader),
            config_file_path=file.absolute().as_posix(),
        )


config: Optional[Config] = None
