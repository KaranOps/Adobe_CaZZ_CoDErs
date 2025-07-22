import pdfplumber
from collections import defaultdict, Counter

# Step 1: Extract all font stats
def extract_font_stats(pdf_path):
    font_stats = defaultdict(lambda: {"count": 0, "sizes": set()})
    all_words = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(extra_attrs=["fontname", "size", "x0", "top"])
            for word in words:
                font = word["fontname"]
                size = float(word["size"])
                font_stats[(font, size)]["count"] += 1
                all_words.append({
                    "text": word["text"],
                    "fontname": font,
                    "size": size,
                    "page": page_num,
                    "x0": word["x0"],
                    "top": word["top"]
                })
    return font_stats, all_words

# Step 2: Determine common font (paragraph)
def get_paragraph_fonts(font_stats):
    font_counts = Counter({k: v["count"] for k, v in font_stats.items()})
    most_common_fonts = font_counts.most_common(1)
    return [most_common_fonts[0][0]] if most_common_fonts else []

# Step 3: Assign semantic tag
def assign_semantic_tags(all_words, para_fonts):
    semantically_tagged = []
    for word in all_words:
        tag = "SPAN"
        font_pair = (word["fontname"], word["size"])

        if font_pair not in para_fonts:
            if word["size"] >= 20:
                tag = "H1"
            elif word["size"] >= 16:
                tag = "H2"
            elif word["size"] >= 13:
                tag = "H3"
        else:
            tag = "P"
        semantically_tagged.append({
            "tag": tag,
            "text": word["text"],
            "page": word["page"],
            "fontname": word["fontname"],
            "size": word["size"],
            "position": {"x0": word["x0"], "top": word["top"]}
        })
    return semantically_tagged

# Step 4: Group by line for readable output (optional)
def group_by_line(tagged_words):
    lines = defaultdict(list)
    for word in tagged_words:
        key = (word["page"], round(word["position"]["top"]))
        lines[key].append(word)
    
    results = []
    for (page, top), line_words in sorted(lines.items()):
        line_words_sorted = sorted(line_words, key=lambda w: w["position"]["x0"])
        full_line = " ".join(w["text"] for w in line_words_sorted)
        tag = line_words_sorted[0]["tag"]  # take tag of first word
        results.append({
            "tag": tag,
            "text": full_line,
            "page": page
        })
    return results

# MAIN
if __name__ == "__main__":
    PDF_PATH = "file01.pdf"  # Change this

    font_stats, all_words = extract_font_stats(PDF_PATH)
    para_fonts = get_paragraph_fonts(font_stats)
    tagged_words = assign_semantic_tags(all_words, para_fonts)
    semantic_lines = group_by_line(tagged_words)

    # Output
    for line in semantic_lines:
        print(f"[{line['tag']}] {line['text']} (page {line['page']})")
