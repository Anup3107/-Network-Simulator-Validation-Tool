# src/parser/config_parser.py
import os
import re

def _to_mbps(bw_str: str) -> int | None:
    """Convert bandwidth string (e.g. '1Gbps', '100Mbps', '200') → Mbps"""
    if not bw_str:
        return None
    s = bw_str.strip().lower()
    m = re.match(r"(\d+(?:\.\d+)?)\s*(g|m)?bps", s)
    if not m:
        try:
            return int(float(s))  # plain number assume Mbps
        except:
            return None
    val, unit = m.groups()
    mbps = float(val) * (1000 if unit == "g" else 1)
    return int(mbps)

def parse_config_file(filepath):
    """Parse a single router dump config file"""
    device = {"name": None, "interfaces": []}

    with open(filepath, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith(("#", "//", ";")):
                continue

            # Router name
            if line.startswith("RouterName"):
                device["name"] = line.split("=", 1)[1].strip()

            # Interface details
            elif line.startswith("Interface"):
                parts = [p.strip() for p in line.split(",")]
                kv = {}
                for p in parts:
                    if "=" in p:
                        k, v = p.split("=", 1)
                        kv[k.strip()] = v.strip()

                iface = {
                    "Interface": kv.get("Interface"),
                    "IP": kv.get("IP"),
                    "BW": kv.get("BW"),
                    "BW_Mbps": _to_mbps(kv.get("BW")),
                    "MTU": int(kv["MTU"]) if kv.get("MTU") else None,
                    "VLAN": int(kv["VLAN"]) if kv.get("VLAN") else None,
                    "Peer": kv.get("Peer"),
                }
                device["interfaces"].append(iface)

    if not device["name"]:
        raise ValueError(f"RouterName missing in {filepath}")

    return device

def parse_all_configs(folder="configs"):
    """Parse all router dump config files (*.dump) in folder"""
    devices = {}
    for file in os.listdir(folder):
        if file.endswith(".dump"):   # ✅ only take .dump files
            dev = parse_config_file(os.path.join(folder, file))
            devices[dev["name"]] = dev
    return devices
