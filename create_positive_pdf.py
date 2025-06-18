from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.multi_cell(0, 10, """\
FPT announces Q1 business results:
- Revenue increased by 15%
- Profit increased by 20% compared to the same period
No bad news, business operations are stable and effective.
""")
pdf.output("docs/fpt_positive.pdf")
print("✅ Tạo file 'docs/fpt_positive.pdf'")
