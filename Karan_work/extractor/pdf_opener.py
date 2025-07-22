import fitz  # PyMuPDF
import re

class PDFTextStyleExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = None

    def open_pdf(self):
        """Open the PDF document for reading."""
        self.doc = fitz.open(self.pdf_path)

    def is_centered(self, bbox, page_width, tolerance=0.1):
        """Check if the text span is approximately centered on the page."""
        center_x = (bbox[0] + bbox[2]) / 2
        page_center = page_width / 2
        return abs(center_x - page_center) < page_width * tolerance

    def extract_text_with_styles(self):
        """
        Extract text spans with detailed metadata:
        - text content
        - font name, font size
        - bold and italic flags
        - bounding box coordinates
        - relative vertical position on page
        - whitespace above (leading space)
        - text pattern indicators (numbering, all caps, keywords)
        - word count, text length
        """
        elements = []
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            page_height = page.rect.height
            page_width = page.rect.width

            blocks = page.get_text("dict")["blocks"]
            prev_span_bottom = 0  # to measure leading whitespace
            span_index = 0

            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text:
                            continue  # skip empty spans
                        bbox = span["bbox"]  # [x0, y0, x1, y1]
                        leading_space = bbox[1] - prev_span_bottom if prev_span_bottom else 0
                        prev_span_bottom = bbox[3]

                        element = {
                            "idx": span_index,
                            "page": page_num + 1,
                            "text": text,
                            "font": span["font"],
                            "size": span["size"],
                            "bold": bool(span["flags"] & 2 ** 4),
                            "italic": bool(span["flags"] & 2 ** 1),
                            "bbox": bbox,
                            "leading_space": leading_space,
                            "relative_y": bbox[1] / page_height,
                            "is_centered": self.is_centered(bbox, page_width),
                            # Text pattern features
                            "is_all_caps": text.isupper() and len(text) > 1,
                            "has_numbering": bool(re.match(r"^\s*\d+(\.\d+)*\s", text)),
                            "has_heading_keywords": bool(re.search(r"\b(introduction|conclusion|summary|section|chapter)\b", text, re.I)),
                            "word_count": len(text.split()),
                            "line_length": len(text)
                        }
                        elements.append(element)
                        span_index += 1
        return elements


if __name__ == "__main__":
    pdf_file = "Untagged-pdf.pdf"  # your test untagged PDF
    extractor = PDFTextStyleExtractor(pdf_file)
    extractor.open_pdf()
    text_spans = extractor.extract_text_with_styles()

    print(f"Extracted {len(text_spans)} text spans from PDF.")
    for span in text_spans[:50]:  # Print first 10 for inspection
        print(span)
