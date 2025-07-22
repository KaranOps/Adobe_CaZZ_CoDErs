import os
from extractor.pdf_opener import PDFTextStyleExtractor
from extractor.body_style import detect_body_style
from extractor.heading_scoring import compute_heading_score
from extractor.outline_builder import assign_heading_levels, build_outline
import json

INPUT_DIR = "input"
OUTPUT_DIR = "output"

def process_pdf(pdf_path, output_path):
    print(f"\n{'='*60}")
    print(f"PROCESSING: {pdf_path}")
    print('='*60)
    
    extractor = PDFTextStyleExtractor(pdf_path)
    extractor.open_pdf()
    text_spans = extractor.extract_text_with_styles()
    
    if not text_spans:
        with open(output_path, "w", encoding="utf-8") as out_f:
            json.dump({"title": "Untitled Document", "outline": []}, out_f)
        return

    body_style = detect_body_style(text_spans)
    body_size = body_style["size"]
    
    print(f"BODY STYLE: Font={body_style['font']}, Size={body_size}, Bold={body_style['bold']}")

    # Score all spans
    for span in text_spans:
        span["heading_score"] = compute_heading_score(span, body_size)

    # DEBUG: Show scores for all spans to identify the threshold issue
    print(f"\nALL TEXT SPANS WITH SCORES:")
    print("-" * 100)
    for i, span in enumerate(text_spans):
        if span["heading_score"] > 0.5:  # Show anything with some score
            print(f"Span {i:3d}: Score={span['heading_score']:5.2f} | Font={span['font']:<15} | Size={span['size']:5.1f} | Bold={span['bold']} | Page={span['page']}")
            print(f"          Text: '{span['text'][:70]}...'")
            if span['text'].lower().startswith('if you'):
                print(f"          *** THIS IS ONE OF YOUR MISSING H3s ***")
            print()

    # Try different thresholds
    print(f"\nTHRESHOLD ANALYSIS:")
    print("-" * 50)
    for threshold in [0.5, 1.0, 1.5, 2.0]:
        candidates = [s for s in text_spans if s["heading_score"] > threshold]
        h3_like = [c for c in candidates if c['text'].lower().startswith('if you')]
        print(f"Threshold > {threshold}: {len(candidates)} total candidates, {len(h3_like)} 'If you...' headings")

    # Use a lower threshold to capture all potential headings
    heading_candidates = [s for s in text_spans if s["heading_score"] > 0.5]  # LOWERED FROM 1.5
    
    print(f"\nFINAL HEADING CANDIDATES ({len(heading_candidates)}):")
    print("-" * 70)
    for i, cand in enumerate(heading_candidates):
        print(f"{i+1:2d}. Score={cand['heading_score']:5.2f} | '{cand['text'][:50]}...' (Page {cand['page']})")

    styles_to_level = assign_heading_levels(heading_candidates)
    assigned_level_count = sum(1 for h in heading_candidates if h.get('level') is not None)
    
    print(f"\nHEADINGS ASSIGNED LEVELS: {assigned_level_count}")
    print("-" * 40)
    for h in heading_candidates:
        if h.get('level'):
            print(f"{h['level']}: '{h['text'][:50]}...' (Page {h['page']})")

    title, outline = build_outline(heading_candidates, styles_to_level)

    print(f"\nFINAL OUTLINE: {len(outline)} headings")
    print("-" * 30)
    for item in outline:
        print(f"{item['level']}: '{item['text'][:50]}...' (Page {item['page']})")

    result = {"title": title, "outline": outline}
    with open(output_path, "w", encoding="utf-8") as out_f:
        json.dump(result, out_f, ensure_ascii=False, indent=2)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("No PDF files found in input directory.")
        return

    for pdf_name in pdf_files:
        pdf_path = os.path.join(INPUT_DIR, pdf_name)
        base_name = os.path.splitext(pdf_name)[0]
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}.json")
        try:
            process_pdf(pdf_path, output_path)
            print(f"\n✓ SUCCESS: Output saved to {output_path}")
        except Exception as e:
            print(f"\n✗ ERROR processing {pdf_name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
