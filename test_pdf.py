from pdfminer.high_level import extract_text
print("pdfminer import ok")
text = extract_text("path/to/sample.pdf")[:300]
print(text)
