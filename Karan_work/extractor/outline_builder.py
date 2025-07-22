from collections import defaultdict
import statistics

def assign_heading_levels(heading_candidates):
    """
    Assigns hierarchical heading levels (H1, H2, H3) based on style prominence.

    Args:
        heading_candidates (list): List of dicts (from scoring step), each with:
            - 'font', 'size', 'bold', 'page', 'relative_y', 'heading_score'

    Returns:
        dict: styles_to_level mapping style tuple -> heading level (H1, H2, H3)
        Additionally, adds a 'level' key to each heading candidate in place.
    """

    # 1. Cluster candidates by style signature (font, rounded size, bold)
    style_groups = defaultdict(list)
    for cand in heading_candidates:
        style_key = (
            cand['font'],
            round(cand['size'], 1),
            cand['bold']
        )
        style_groups[style_key].append(cand)

    # 2. Compute stats per style cluster and sort clusters by size then avg score
    cluster_stats = []
    for style_key, group in style_groups.items():
        scores = [c['heading_score'] for c in group]
        avg_score = statistics.mean(scores)
        median_score = statistics.median(scores)
        std_dev_score = statistics.stdev(scores) if len(scores) > 1 else 0.0
        
        cluster_stats.append({
            "style_key": style_key,
            "font": style_key[0],
            "size": style_key[1],
            "bold": style_key[2],
            "avg_score": avg_score,
            "median_score": median_score,
            "std_dev_score": std_dev_score,
            "group_size": len(group),
            "candidates": group,
        })

    # Sort descending by font size, then avg_score, then bold flag
    cluster_stats.sort(key=lambda x: (-x['size'], -x['avg_score'], -int(x['bold'])))

    # Optional: print style cluster stats for debugging
    print("\nHeading Style Clusters Statistics:")
    print("{:<30} {:>6} {:>8} {:>8} {:>8}".format("Style (Font, Size, Bold)", "Count", "Mean", "Median", "StdDev"))
    for cluster in cluster_stats:
        style = cluster['style_key']
        print(f"{style[0]}, {style[1]:.1f}pt, Bold={style[2]!s:<3}  "
              f"{cluster['group_size']:6d}  "
              f"{cluster['avg_score']:8.3f}  "
              f"{cluster['median_score']:8.3f}  "
              f"{cluster['std_dev_score']:8.3f}")

    # 3. Assign H1, H2, H3 to top three style clusters
    styles_to_level = {}
    for idx, cluster in enumerate(cluster_stats[:3]):
        level = f"H{idx+1}"
        styles_to_level[cluster['style_key']] = level
        for cand in cluster['candidates']:
            cand['level'] = level

    # 4. Assign None level to all candidates from other style clusters
    for cluster in cluster_stats[3:]:
        for cand in cluster['candidates']:
            cand['level'] = None

    return styles_to_level


def build_outline(heading_candidates, styles_to_level):
    """
    Builds the JSON outline with consistent ordering and title selection.

    Args:
        heading_candidates (list): List of dicts with 'level' assigned (H1, H2, H3 or None)

    Returns:
        tuple: (title, outline) where
            title (str): Document title,
            outline (list): List of dicts {level, text, page}
    """
    # Extract all candidates assigned a heading level
    headings = [c for c in heading_candidates if c.get('level') in ("H1", "H2", "H3")]

    # Sort all headings by page number, then vertical position
    headings.sort(key=lambda x: (x['page'], x['relative_y']))

    # Identify title as the first/topmost H1 near the top of the first page
    title = None
    title_to_remove = None
    h1_candidates = [h for h in headings if h['level'] == 'H1' and h['page'] == 1]

    if h1_candidates:
        h1_candidates.sort(key=lambda h: (h['relative_y'], -h['heading_score']))
        if h1_candidates[0]['relative_y'] <= 0.2:
            title = h1_candidates[0]['text']
            title_to_remove = h1_candidates[0]

    # If no title found, fallback to first H1 in entire outline
    if not title:
        for h in headings:
            if h['level'] == "H1":
                title = h['text']
                title_to_remove = h
                break

    if not title:
        title = "Untitled Document"

    # Remove the specific title instance using unique identifier (idx) if possible
    if title_to_remove and title_to_remove.get('idx') is not None:
        headings = [h for h in headings if h.get('idx') != title_to_remove.get('idx')]

    # Prepare the outline list
    outline = [{
        "level": h['level'],
        "text": h['text'],
        "page": h['page'],
    } for h in headings]

    return title, outline
