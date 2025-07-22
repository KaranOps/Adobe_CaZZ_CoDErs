import os
from extractor.pdf_opener import PDFTextStyleExtractor
from extractor.body_style import detect_body_style
from extractor.heading_scoring import score_headings
from extractor.outline_builder import assign_levels_and_outline, write_outline_to_json

INPUT_DIR = "input"
OUTPUT_DIR = "output"

def process_all_pdfs():
    # Make sure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # List all PDF files in input folder
    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(INPUT_DIR, filename)
            json_path = os.path.join(OUTPUT_DIR, filename.rsplit(".", 1)[0] + ".json")
            print(f"Processing: {filename}")

            # Step 1: Extract spans
            extractor = PDFTextStyleExtractor(pdf_path)
            extractor.open_pdf()
            text_spans = extractor.extract_text_styles()

            # Step 2: Detect body style
            body_style = detect_body_style(text_spans)

            # Step 3: Score headings
            candidates = score_headings(text_spans, body_style)

            # Step 4: Assign heading levels and create outline
            title, outline = assign_levels_and_outline(candidates)

            # Step 5: Write output JSON
            write_outline_to_json(title, outline, json_path)

            print(f"Wrote outline to: {json_path}")

if __name__ == "__main__":
    process_all_pdfs()
