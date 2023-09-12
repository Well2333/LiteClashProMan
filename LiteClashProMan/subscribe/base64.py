import base64
import json
from typing import TypedDict

from .clash import SS, Vmess


def ss(sub: str) -> "SS":
    """Format the ShadowSocks proxy like ss://{base64encode}#{name}@{server}:{port}"""
    base64_encoded, name_and_other = sub[5:].split("#")

    cipher_password, server_and_port = (
        base64.b64decode(f"{base64_encoded}===").decode().split("@")
    )
    cipher, password = cipher_password.split(":")

    server, port = server_and_port.split(":")
    name = "JMS-" + name_and_other.split("@")[1].split(".")[0]

    return SS(
        name=name,
        server=server,
        type="ss",
        port=int(port),
        cipher=cipher,
        password=password,
        udp=True,
    )


class VmessRaw(TypedDict):
    ps: str
    port: str
    id: str
    aid: int
    net: str
    type: str
    tls: str
    add: str


def vmess(sub: str) -> "Vmess":
    """Format the Vmess proxy like vmess://{base64encode}"""

    decoded_sub = base64.b64decode(f"{sub[8:]}===").decode()
    vmess_raw = json.loads(decoded_sub)

    server_address = vmess_raw["add"]
    port = int(vmess_raw["port"])
    uuid = vmess_raw["id"]
    alter_id = vmess_raw["aid"]
    tls_enabled = vmess_raw["tls"] != "none"

    se_name = str(vmess_raw["ps"]).split("@")[1].split(":")[0]
    name = "JMS-" + se_name.split(".")[0]

    return Vmess(
        name=name,
        server=server_address,
        port=port,
        type="vmess",
        uuid=uuid,
        alterId=alter_id,
        cipher="auto",
        tls=tls_enabled,
        skip_cert_verify=True,
        udp=False,
    )
