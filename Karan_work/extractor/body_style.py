from collections import Counter
import re

def detect_body_style(text_spans):
    """
    Detect the document's body text style using character count aggregation.
    Rule: If a bold style has the same font size as non-bold style,
    consider the non-bold style as body text.
    """
    style_counts = Counter()
    for span in text_spans:
        key = (
            span['font'],
            round(span['size'], 1),
            span.get('bold', False),
            span.get('italic', False)
        )
        style_counts[key] += len(span['text'])

    sorted_styles = style_counts.most_common()
    if not sorted_styles:
        return {'font': '', 'size': 12.0, 'bold': False, 'italic': False}

    # Pick highest counted style tentatively
    body_style = sorted_styles[0][0]

    # Check for non-bold style of same font size to prefer as body
    if body_style[2]:  # If bold
        for style, count in sorted_styles[1:]:
            if style[1] == body_style[1] and not style[2]:
                # If non-bold style with same size has sufficient representation
                if count >= sorted_styles[0][1] * 0.5:
                    body_style = style
                    break

    return {
        'font': body_style[0],
        'size': body_style[1],
        'bold': body_style[2],
        'italic': body_style[3]
    }
