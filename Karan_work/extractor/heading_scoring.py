import re

def score_headings(text_spans, body_style):
    """
    Assigns a heading score to each span using multi-factor weights.
    Returns a list of dicts with heading candidates and their scores.
    """
    scored = []

    for span in text_spans:
        score = 0
        # Font size prominence
        if span['size'] > body_style['size'] * 1.1:
            score += 2

        # Boldness/Italics
        if span.get('bold') and not body_style['bold']:
            score += 1.5
        if span.get('italic') and not body_style['italic']:
            score += 0.5

        # Different font family
        if span['font'] != body_style['font']:
            score += 1

        # Centered or isolated lines (example - you can expand)
        if 'bbox' in span and abs((span['bbox'][0]+span['bbox'][2])/2 - 300) < 50:
            score += 0.5

        # All caps, numbered, heading-like words
        txt = span['text']
        if txt.isupper() and len(txt) > 2:
            score += 0.7
        if re.match(r"^\d+(\.\d+)*\s", txt):
            score += 1
        if re.search(r'\b(introduction|summary|section|chapter|conclusion|references)\b', txt.lower()):
            score += 0.8

        # Short lines typical for headings
        if 1 <= len(txt.split()) <= 8:
            score += 0.5
        elif len(txt.split()) > 15:
            score -= 1

        if score > 1:  # Candidate if above a threshold (tune as needed)
            scored.append({
                "idx": span.get("idx"),
                "page": span.get("page"),
                "text": txt,
                "score": score,
                "style": {
                    "font": span["font"],
                    "size": span["size"],
                    "bold": span.get("bold"),
                    "italic": span.get("italic"),
                }
            })

    return scored
