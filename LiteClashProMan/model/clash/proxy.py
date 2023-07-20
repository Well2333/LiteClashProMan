from typing import Literal, Optional

from pydantic import BaseModel, Extra, Field, validator


class SS(BaseModel, extra=Extra.allow):
    name: str
    type: Literal["ss"] = "ss"
    server: str
    port: int
    cipher: Literal[
        "aes-128-gcm",
        "aes-192-gcm",
        "aes-256-gcm",
        "aes-128-cfb",
        "aes-192-cfb",
        "aes-256-cfb",
        "aes-128-ctr",
        "aes-192-ctr",
        "aes-256-ctr",
        "rc4-md5",
        "chacha20-ietf",
        "xchacha20",
        "chacha20-ietf-poly1305",
        "xchacha20-ietf-poly1305",
    ]
    password: str
    udp: Optional[bool] = False


class SSR(SS):
    type: Literal["ssr"] = "ssr"
    obfs: Literal[
        "plain",
        "http_simple",
        "http_post",
        "random_head",
        "tls1.2_ticket_auth",
        "tls1.2_ticket_fastauth",
    ]
    protocol: Literal[
        "origin",
        "auth_sha1_v4",
        "auth_aes128_md5",
        "auth_aes128_sha1",
        "auth_chain_a",
        "auth_chain_b",
    ]
    obfs_param: Optional[str] = Field(default=None, alias="obfs-param")
    protocol_param: Optional[str] = Field(default=None, alias="protocol-param")
    udp: Optional[bool] = False


class Vmess(BaseModel, extra=Extra.allow):
    name: str
    type: Literal["vmess"] = "vmess"
    server: str
    port: int
    uuid: str
    alterId: int
    cipher: Literal["auto", "aes-128-gcm", "chacha20-poly1305", "none"] = "auto"


class Socks5(BaseModel, extra=Extra.allow):
    name: str
    type: Literal["socks5"] = "socks5"
    server: str
    port: int


class Snell(BaseModel, extra=Extra.allow):
    name: str
    type: Literal["snell"] = "snell"
    server: str
    port: int
    psk: str


class Trojan(BaseModel, extra=Extra.allow):
    name: str
    type: Literal["trojan"] = "trojan"
    server: str
    port: int
    password: str
