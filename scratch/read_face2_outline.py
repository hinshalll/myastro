import os
import pypdf

pdf_path = r"C:\Users\hinsh\Downloads\face2.pdf"
if not os.path.exists(pdf_path):
    print("face2.pdf not found!")
    exit(1)

reader = pypdf.PdfReader(pdf_path)
num_pages = len(reader.pages)
print(f"face2.pdf has {num_pages} pages.")

# Let's read first page and any outline
outline = reader.outline
print(f"Outline length: {len(outline) if outline else 0}")

# Extract first 3 pages
text = ""
for i in range(min(5, num_pages)):
    t = reader.pages[i].extract_text()
    if t:
        text += f"--- Page {i+1} ---\n" + t + "\n"

print("First few pages of face2.pdf:")
print(text[:2000])

with open(r"C:\Users\hinsh\Desktop\myastro\scratch\face2_intro.txt", "w", encoding="utf-8") as f:
    f.write(text)
