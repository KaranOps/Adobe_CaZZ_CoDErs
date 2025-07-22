import re

def compute_heading_score(span, body_style_size):
    """
    Compute a heading score for a text span using multiple features and weighted factors.

    Args:
        span (dict): text span metadata, with keys:
            - size (float): font size
            - bold (bool): bold style flag
            - leading_space (float): whitespace in points above this line
            - text (str): text content
            - relative_y (float): normalized vertical position (0=top)
            - has_numbering (bool): if text starts with numbering e.g. "1.", "2.1"
            - has_heading_keywords (bool): presence of words like 'introduction'
            - word_count (int): number of words in text

        body_style_size (float): font size for the detected body text baseline.

    Returns:
        float: computed heading score
    """

    score = 0.0

    # 1. Font size ratio (weight 2.0)
    if body_style_size > 0:
        size_ratio = span['size'] / body_style_size
    else:
        size_ratio = 1.0  # avoid division by zero
    
    if size_ratio > 1.0:
        # Proportional score with limit to avoid bias from outliers
        capped_ratio = min(size_ratio, 2.0)
        score += 2.0 * (capped_ratio - 1.0)

    # 2. Boldness (weight 0.8)
    # Only count bold bonus if font size is larger than body text size (strict requirement)
    if span.get('bold', False) and size_ratio > 1.0:
        score += 0.8

    # 3. Leading whitespace (vertical space above line) (weight 1.0)
    if span.get('leading_space', 0) > 10:  # Threshold in points; tune if needed
        score += 1.0

    # 4. Text length penalty for long lines (weight -1.0)
    word_count = span.get('word_count', len(span.get('text', '').split()))
    if word_count > 15:
        score -= 1.0

    # 5. Position on page (title likely near top) (weight 1.5)
    relative_y = span.get('relative_y', 1.0)
    if 0 <= relative_y < 0.2:
        score += 1.5

    # 6. Numbering pattern at start (weight 1.2)
    if span.get('has_numbering', False):
        score += 1.2

    # 7. Heading keyword presence (weight 1.0)
    if span.get('has_heading_keywords', False):
        score += 1.0

    return score
