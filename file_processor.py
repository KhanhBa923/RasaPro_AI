import os
import time
from pathlib import Path
import PyPDF2
from docx import Document
import pandas as pd

# Thư mục input và output
input_folder = Path("./raw_docs")
output_folder = Path("./docs")
output_folder.mkdir(exist_ok=True)

# Các hàm trích xuất văn bản từ các định dạng
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in pdf_reader.pages)

def extract_text_from_word(docx_path):
    doc = Document(docx_path)
    text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            text += "\n" + " | ".join(cell.text for cell in row.cells)
    return text

def extract_text_from_excel(excel_path):
    excel_file = pd.ExcelFile(excel_path)
    text = ""
    for sheet in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet)
        text += f"\n--- Sheet: {sheet} ---\n"
        text += " | ".join(df.columns.astype(str)) + "\n"
        for _, row in df.iterrows():
            text += " | ".join(row.astype(str)) + "\n"
    return text

# Bộ xử lý file theo phần mở rộng
file_processors = {
    '.pdf': extract_text_from_pdf,
    '.docx': extract_text_from_word,
    '.doc': extract_text_from_word,
    '.xlsx': extract_text_from_excel,
    '.xls': extract_text_from_excel
}

# Xử lý các file
for file_path in input_folder.glob("*"):
    ext = file_path.suffix.lower()
    if ext in file_processors:
        try:
            text = file_processors[ext](file_path)
            base_name = file_path.stem
            output_file = output_folder / f"{base_name}.txt"
            timestamp = time.strftime("%Y%m%d%H%M%S")
            output_file = output_folder / f"{base_name}_{timestamp}.txt"

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"✅ Đã xử lý: {file_path.name}")
        except Exception as e:
            print(f"❌ Lỗi xử lý {file_path.name}: {e}")
    else:
        print(f"⚠️ Định dạng không hỗ trợ: {file_path.name}")
