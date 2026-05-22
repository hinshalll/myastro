import os
import sys

# Try imports
pdf_libraries = ['pypdf', 'PyPDF2', 'fitz', 'pdfplumber', 'pdfminer']
installed = []
for lib in pdf_libraries:
    try:
        __import__(lib)
        installed.append(lib)
    except ImportError:
        pass

print(f"Installed PDF libraries: {installed}")

pdf_path = r"C:\Users\hinsh\Downloads\face1.pdf"
if not os.path.exists(pdf_path):
    print("face1.pdf not found!")
    sys.exit(1)

text = ""
if 'pypdf' in installed:
    import pypdf
    reader = pypdf.PdfReader(pdf_path)
    for i, page in enumerate(reader.pages):
        t = page.extract_text()
        if t:
            text += f"--- Page {i+1} ---\n" + t + "\n"
elif 'PyPDF2' in installed:
    import PyPDF2
    reader = PyPDF2.PdfReader(pdf_path)
    for i, page in enumerate(reader.pages):
        t = page.extract_text()
        if t:
            text += f"--- Page {i+1} ---\n" + t + "\n"
elif 'fitz' in installed:
    import fitz
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        text += f"--- Page {i+1} ---\n" + page.get_text() + "\n"
else:
    # Let's try importing pypdf or PyPDF2 via pip if needed, but let's first check if we can run this.
    print("No native PDF library available. Let's try importing what we can or installing pypdf.")

if text:
    print(f"Successfully extracted {len(text)} characters from face1.pdf")
    # print first 1500 chars
    print(text[:1500])
    
    # Save the output
    with open(r"C:\Users\hinsh\Desktop\myastro\scratch\face1_extracted.txt", "w", encoding="utf-8") as f:
        f.write(text)
else:
    print("Failed to extract text from face1.pdf")
