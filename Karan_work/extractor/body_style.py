from collections import Counter

def detect_body_style(text_spans):
    """
    Given extracted text spans, find the most common (font, size, bold/italic)
    style — assumed body text baseline.
    """
    style_counter = Counter()
    for span in text_spans:
        style_key = (
            span['font'],
            round(span['size'], 1),
            span.get('bold', False),
            span.get('italic', False)
        )
        style_counter[style_key] += len(span['text'] or "")

    most_common_style, _ = style_counter.most_common(1)[0]
    return {
        "font": most_common_style[0],
        "size": most_common_style[1],
        "bold": most_common_style[2],
        "italic": most_common_style[3]
    }
