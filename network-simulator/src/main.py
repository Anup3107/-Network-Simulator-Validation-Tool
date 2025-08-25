import argparse
import matplotlib.pyplot as plt
import networkx as nx

from src.parser.config_parser import parse_all_configs
from src.topology.graph_builder import build_topology
from src.validation.validator import validate_all, pretty_print_report
from src.report import generate_pdf_report


def main():
    parser = argparse.ArgumentParser(description="Network Topology Tool")
    parser.add_argument("--configs", default="configs", help="Configs folder path")
    parser.add_argument("--draw", action="store_true", help="Draw topology graph")
    parser.add_argument("--validate", action="store_true", help="Run validation checks")
    parser.add_argument("--report", action="store_true", help="Generate PDF report")
    args = parser.parse_args()

    # Step 1: Parse configs
    devices = parse_all_configs(args.configs)

    # Step 2: Run validations
    report = validate_all(devices)
    summary_text = pretty_print_report(report, return_text=True) if args.validate or args.report else ""

    # Step 3: Draw topology graph (always if report/draw is requested)
    graph_path = None
    if args.draw or args.report:
        G = build_topology(devices)
        pos = nx.spring_layout(G, seed=42)

        node_colors, node_borders, edge_colors, edge_styles = [], [], [], {}

        dup_nodes = {d for uses in report["duplicate_ips"].values() for d, _ in uses}
        invalid_vlan_nodes = {d for d, _, _ in report["invalid_vlans"]}
        mismatch_edges = {(a, b) for a, b, _, _ in report["mtu_mismatches"]}
        loop_edges = {
            tuple(sorted((cycle[i], cycle[(i + 1) % len(cycle)])))
            for cycle in report["loops"] for i in range(len(cycle))
        }

        for node in G.nodes():
            node_colors.append("red" if node in dup_nodes else "lightblue")
            node_borders.append("orange" if node in invalid_vlan_nodes else "black")

        for u, v in G.edges():
            key = tuple(sorted((u, v)))
            edge_colors.append("red" if key in mismatch_edges else "gray")
            edge_styles[(u, v)] = "dashed" if key in loop_edges else "solid"

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, edgecolors=node_borders, node_size=2000, linewidths=2)
        nx.draw_networkx_labels(G, pos, font_size=10, font_color="black")

        for (u, v), style in edge_styles.items():
            nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=[edge_colors[list(G.edges()).index((u, v))]], style=style, width=2)

        nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, "bw"))
        plt.title("Network Topology with Validation Highlights")

        graph_path = "topology.png"
        plt.savefig(graph_path, dpi=300, bbox_inches="tight")
        if args.draw:
            plt.show()
        else:
            plt.close()

    # Step 4: Generate PDF Report
    if args.report:
        generate_pdf_report(summary_text, graph_path, "Network_Report.pdf")


if __name__ == "__main__":
    main()
