import pdfplumber
from collections import defaultdict

font_stats = defaultdict(lambda: {"count": 0, "sizes": set()})

with pdfplumber.open("file03.pdf") as pdf:
    for page in pdf.pages:
        for word in page.extract_words(extra_attrs=["fontname", "size"]):
            key = word["fontname"]
            font_stats[key]["count"] += 1
            font_stats[key]["sizes"].add(word["size"])

# Display font families, size ranges and frequency
for fontname, data in font_stats.items():
    print(f"{fontname}: used {data['count']} times, sizes: {sorted(data['sizes'])}")
