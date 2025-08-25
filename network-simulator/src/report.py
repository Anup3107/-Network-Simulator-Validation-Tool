from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import os

def generate_pdf_report(summary_text, graph_path, output_path="Network_Report.pdf"):
    """Generate a PDF report with validation summary and network graph"""
    # PDF document setup
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Title
    story.append(Paragraph("<b>Network Validation Report</b>", styles["Title"]))
    story.append(Spacer(1, 20))

    # Summary Section
    story.append(Paragraph("<b>Validation Summary:</b>", styles["Heading2"]))
    if summary_text:
        for line in summary_text.split("\n"):
            if line.strip():
                story.append(Paragraph(line, styles["Normal"]))
    else:
        story.append(Paragraph("No validation summary generated.", styles["Normal"]))
    story.append(Spacer(1, 20))

    # Graph Section
    if graph_path and os.path.exists(graph_path):
        abs_path = os.path.abspath(graph_path)  # ✅ Absolute path
        story.append(Paragraph("<b>Network Topology:</b>", styles["Heading2"]))
        story.append(Spacer(1, 10))
        story.append(Image(abs_path, width=400, height=300))  # ✅ Use abs_path
    else:
        story.append(Paragraph("⚠️ Topology image not found.", styles["Normal"]))

    # Build PDF
    doc.build(story)
    print(f"✅ PDF report generated: {output_path}")
