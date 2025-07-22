def assign_levels_and_outline(candidates):
    """
    Inputs:
        - candidates: List of dicts {'text', 'score', 'font', 'size', ...}
    Outputs:
        - title: str
        - outline: List of {level, text, page}
    """
    # 1. Cluster by (font, size, bold) and score
    style_clusters = {}
    for c in candidates:
        style_key = (c['style']['font'], round(c['style']['size'], 1), c['style']['bold'])
        style_clusters.setdefault(style_key, []).append(c)

    # 2. Sort clusters by average score/size
    sorted_clusters = sorted(
        style_clusters.items(),
        key=lambda x: (-sum(cc['score'] for cc in x[1]) / len(x[1]), -x[1][0]['style']['size'])
    )

    # 3. Assign levels
    heading_levels = {}
    for i, (style_key, cluster) in enumerate(sorted_clusters[:3]):  # Only three levels
        heading_levels[style_key] = f"H{i+1}"

    # 4. Build ordered outline
    ordered = sorted(candidates, key=lambda c: (c['page'], c.get('y_position', 0)))
    outline = []
    title = None
    for c in ordered:
        style_key = (c['style']['font'], round(c['style']['size'], 1), c['style']['bold'])
        level = heading_levels.get(style_key)
        if not level: continue
        # First very prominent heading is likely the title
        if not title and level == "H1" and c['score'] > 3.0:
            title = c["text"]
            continue
        outline.append({
            "level": level,
            "text": c["text"],
            "page": c["page"]
        })
    return title or "Untitled", outline

import json
import os

def write_outline_to_json(title, outline, output_path):
    """
    Write the document outline to a JSON file following the required schema.
    Args:
        title (str): The detected document title.
        outline (list): List of dicts with structure [{level, text, page}, ...].
        output_path (str): The output .json file path.
    """
    output_data = {
        "title": title,
        "outline": outline
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)