import base64
import json

from .clash import SS, Vmess


def ss(sub: str) -> "SS":
    """Format the ShadowSocks proxy like ss://{base64encode}#{name}@{server}:{port}"""
    ci_pa, se_po = sub[5:].split("#")

    ci_pa = base64.b64decode(f"{ci_pa}===").decode().split("@")[0]
    ci, pa = ci_pa.split(":")

    se, po = se_po.split("@")[1].split(":")
    na = "JMS-" + se.split(".")[0]

    return SS(
        **{
            "name": na,
            "server": se,
            "type": "ss",
            "port": int(po),
            "cipher": ci,
            "password": pa,
            "udp": True,
        }
    )


def vmess(sub: str) -> "Vmess":
    """Format the Vmess proxy like vmess://{base64encode}"""
    vmess = json.loads(base64.b64decode(f"{sub[8:]}===").decode())

    se = str(vmess["ps"]).split("@")[1].split(":")[0]
    na = "JMS-" + se.split(".")[0]

    return Vmess(
        **{
            "name": na,
            "server": se,
            "port": int(vmess["port"]),
            "type": "vmess",
            "uuid": vmess["id"],
            "alterId": vmess["aid"],
            "cipher": "auto",
            "tls": vmess["tls"] != "none",
            "skip-cert-verify": True,
            "udp": True,
        }
    )
