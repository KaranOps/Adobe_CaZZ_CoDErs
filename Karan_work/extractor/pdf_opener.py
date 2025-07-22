# Open PDF and Collect Raw Text + Style Metadata
import fitz  # PyMuPDF

class PDFTextStyleExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = None

    def open_pdf(self):
        """Opens the PDF and prepares for parsing."""
        self.doc = fitz.open(self.pdf_path)

    def extract_text_styles(self):
        """
        Go through each page and collect:
        - Text of each span
        - Font name
        - Font size
        - Font flags (bold, italic)
        - Bounding box (location on page)
        - Page number
        """
        all_elements = []
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        element = {
                            "page": page_num + 1,  # 1-based indexing
                            "text": span["text"].strip(),
                            "font": span["font"],
                            "size": span["size"],
                            "bold": bool(span["flags"] & 2**4),
                            "italic": bool(span["flags"] & 2**1),
                            "bbox": span["bbox"],  # x0, y0, x1, y1
                        }
                        if element["text"]:  # Ignore empty/whitespace
                            all_elements.append(element)
        return all_elements
    
def get_pdf_elements(pdf_path):
    extractor = PDFTextStyleExtractor(pdf_path)
    extractor.open_pdf()
    elements = extractor.extract_text_styles()
    return elements

if __name__ == "__main__":
    file = "Untagged-pdf.pdf"
    results = get_pdf_elements(file)
    print(results[:50])  # Print first 5 items for review

