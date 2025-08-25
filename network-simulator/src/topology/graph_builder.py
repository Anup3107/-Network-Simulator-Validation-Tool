import networkx as nx

def build_topology(devices):
    """Convert parsed devices into a NetworkX topology graph"""
    G = nx.Graph()
    for dev_name, dev in devices.items():
        G.add_node(dev_name)
        for iface in dev.get("interfaces", []):
            peer = iface.get("Peer")
            if peer:
                G.add_edge(
                    dev_name,
                    peer,
                    bw=iface.get("BW"),
                    bw_mbps=iface.get("BW_Mbps"),
                )
    return G
