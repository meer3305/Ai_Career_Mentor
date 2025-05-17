from fpdf import FPDF
import uuid

def create_pdf(summary, filename=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for section, content in summary.items():
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(200, 10, txt=section, ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=content)
        pdf.ln()

    if filename is None:
        filename = f"interview_report_{uuid.uuid4().hex[:8]}.pdf"
    pdf.output(filename)
    return filename
