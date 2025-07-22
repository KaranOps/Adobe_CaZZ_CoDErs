import pdfplumber

pdf_path = "file05.pdf"

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages):
        print(f"\nPage {page_num + 1}")
        for obj in page.extract_words(extra_attrs=["fontname", "size"]):
            print({
                "text": obj["text"],
                "fontname": obj["fontname"],
                "fontsize": obj["size"],
                "x": obj["x0"],
                "y": obj["top"],
            })
