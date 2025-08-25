from collections import defaultdict
import networkx as nx
from src.topology.graph_builder import build_topology


def find_duplicate_ips(devices):
    bucket = defaultdict(list)
    for dname, dev in devices.items():
        for iface in dev.get("interfaces", []):
            ip = iface.get("IP")
            vlan = iface.get("VLAN")
            if ip and vlan is not None:
                bucket[(vlan, ip)].append((dname, iface.get("Interface")))
    return {k: v for k, v in bucket.items() if len(v) > 1}


def find_invalid_vlans(devices):
    invalid = []
    for dname, dev in devices.items():
        for iface in dev.get("interfaces", []):
            vlan = iface.get("VLAN")
            if vlan is not None and not (1 <= int(vlan) <= 4094):
                invalid.append((dname, iface.get("Interface"), vlan))
    return invalid


def find_mtu_mismatches(devices):
    seen = set()
    mismatches = []
    for a_name, a_dev in devices.items():
        for a_if in a_dev.get("interfaces", []):
            b_name = a_if.get("Peer")
            if not b_name or b_name not in devices:
                continue
            b_dev = devices[b_name]
            b_if = next((x for x in b_dev.get("interfaces", [])
                         if x.get("Peer") == a_name), None)
            if not b_if:
                continue
            a_mtu, b_mtu = a_if.get("MTU"), b_if.get("MTU")
            if a_mtu is not None and b_mtu is not None and a_mtu != b_mtu:
                key = tuple(sorted([a_name, b_name]))
                if key not in seen:
                    seen.add(key)
                    mismatches.append((key[0], key[1], a_mtu, b_mtu))
    return mismatches


def find_missing_peers(devices):
    names = set(devices.keys())
    missing = []
    for dname, dev in devices.items():
        for iface in dev.get("interfaces", []):
            peer = iface.get("Peer")
            if peer and peer not in names:
                missing.append((dname, iface.get("Interface"), peer))
    return missing


def find_loops(devices):
    G = build_topology(devices)
    return nx.cycle_basis(G)


def validate_all(devices):
    return {
        "duplicate_ips": find_duplicate_ips(devices),
        "invalid_vlans": find_invalid_vlans(devices),
        "mtu_mismatches": find_mtu_mismatches(devices),
        "missing_peers": find_missing_peers(devices),
        "loops": find_loops(devices),
    }


def pretty_print_report(report, return_text=False):
    """Print to console and optionally return summary string"""
    lines = ["==== Validation Report ===="]

    if report["duplicate_ips"]:
        lines.append("\nDuplicate IPs (same VLAN):")
        for (vlan, ip), uses in report["duplicate_ips"].items():
            locs = ", ".join([f"{d}:{i}" for d, i in uses])
            lines.append(f"  VLAN {vlan} IP {ip} -> {locs}")
    else:
        lines.append("\nDuplicate IPs: NONE")

    if report["invalid_vlans"]:
        lines.append("\nInvalid VLANs:")
        for dev, iface, vlan in report["invalid_vlans"]:
            lines.append(f"  {dev}:{iface} -> VLAN {vlan}")
    else:
        lines.append("\nInvalid VLANs: NONE")

    if report["mtu_mismatches"]:
        lines.append("\nMTU mismatches:")
        for a, b, a_mtu, b_mtu in report["mtu_mismatches"]:
            lines.append(f"  {a} <-> {b} : {a_mtu} vs {b_mtu}")
    else:
        lines.append("\nMTU mismatches: NONE")

    if report["missing_peers"]:
        lines.append("\nMissing peer configs:")
        for dev, iface, peer in report["missing_peers"]:
            lines.append(f"  {dev}:{iface} -> Peer '{peer}' not found")
    else:
        lines.append("\nMissing peer configs: NONE")

    if report["loops"]:
        lines.append("\nLoops detected (node cycles):")
        for cycle in report["loops"]:
            lines.append("  - " + " -> ".join(cycle) + f" -> {cycle[0]}")
    else:
        lines.append("\nLoops: NONE")

    final_text = "\n".join(lines)

    # Always print to console
    print(final_text)

    if return_text:
        return final_text
    return ""
