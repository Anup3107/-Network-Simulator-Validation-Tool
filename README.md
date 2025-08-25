# -Network-Simulator-Validation-Tool
This project is a **Cisco-like Network Topology Simulator** that:   - Parses device configuration files   - Builds a topology graph   - Validates configurations (duplicate IPs, MTU mismatches, invalid VLANs, loops)   - Visualizes the network graph with highlights   - Generates a **PDF Report** with validation summary and graph

## 🚀 Features
- Parse configs from `configs/` folder  
- Build topology graph using **NetworkX**  
- Validation checks:  
  - Duplicate IP detection  
  - MTU mismatch  
  - VLAN validation  
  - Loop detection  
- Draw topology graph with highlights  
- Export **Network_Report.pdf**

## 📌 Requirements
- Python 3.9+
- Libraries:
- matplotlib
- networkx
- reportlab

**pip install matplotlib networkx reportlab**

## Run with validation + graph + PDF report

**python -m src.main --configs configs --draw --report**

**📝 Example Output**

Topology Graph:
-Duplicate IPs → 🔴 red nodes
-Invalid VLANs → 🟠 orange borders
-MTU mismatches → 🔴 red edges
-Loops → 🔀 dashed edges
-PDF Report (Network_Report.pdf):
-Validation Summary
-Network Topology Graph
