import pypdf

reader = pypdf.PdfReader(r"C:\Users\hinsh\Downloads\face2.pdf")
text_found = False
for idx, page in enumerate(reader.pages):
    t = page.extract_text()
    if t and len(t.strip()) > 50:
        print(f"Found text on page {idx+1}: {t[:300]}...")
        text_found = True
        break

if not text_found:
    print("No searchable text found in face2.pdf (it is likely scanned images).")
