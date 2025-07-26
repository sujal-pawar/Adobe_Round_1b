from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("helvetica", size=16)  # Changed from Arial to helvetica (built-in font)

# Add "1 Introduction" section
pdf.cell(200, 10, txt="1 Introduction", ln=True)
pdf.set_font("helvetica", size=12)
pdf.multi_cell(0, 10, txt="This is the introduction section describing the background.")

# Add "2 Related Work" section
pdf.set_font("helvetica", size=16)
pdf.cell(200, 10, txt="2 Related Work", ln=True)
pdf.set_font("helvetica", size=12)
pdf.multi_cell(0, 10, txt="Summary of previous research relevant to our topic.")

pdf.output("test_pdfs/sample.pdf")