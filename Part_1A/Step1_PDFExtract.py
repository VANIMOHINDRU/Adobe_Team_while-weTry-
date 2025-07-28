import fitz  # PyMuPDF
import os
import json
import re
from collections import defaultdict

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    text_blocks = []

    # Step 1: Extract all text blocks
    for page_num, page in enumerate(doc, start=1):
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    line_text = ""
                    line_size = 0
                    line_flags = 0
                    span_count = 0

                    for span in line["spans"]:
                        line_text += span["text"]
                        line_size += span["size"]
                        line_flags |= span["flags"]
                        span_count += 1

                    if line_text.strip() and span_count > 0:
                        text_blocks.append({
                            "text": line_text.strip(),
                            "size": round(line_size / span_count, 1),
                            "page": page_num,
                            "flags": line_flags,
                            "bbox": line["bbox"]
                        })

    doc.close()

    # Step 2: Merge multi-line headings
    def can_merge_blocks(a, b):
        same_page = a["page"] == b["page"]
        size_match = abs(a["size"] - b["size"]) < 0.5
        left_aligned = abs(a["bbox"][0] - b["bbox"][0]) < 5
        vertical_gap = b["bbox"][1] - a["bbox"][3]
        close_enough = 0 < vertical_gap < 12
        combined_len = len((a["text"] + " " + b["text"]).strip())

        return same_page and size_match and left_aligned and close_enough and combined_len < 150

    merged = []
    i = 0
    while i < len(text_blocks) - 1:
        a, b = text_blocks[i], text_blocks[i + 1]
        if can_merge_blocks(a, b):
            merged.append({
                "text": a["text"] + " " + b["text"],
                "size": a["size"],
                "page": a["page"],
                "flags": a["flags"] | b["flags"],
                "bbox": (a["bbox"][0], a["bbox"][1], max(a["bbox"][2], b["bbox"][2]), b["bbox"][3])
            })
            i += 2
        else:
            merged.append(a)
            i += 1
    if i == len(text_blocks) - 1:
        merged.append(text_blocks[-1])
    text_blocks = merged

    # Step 3: Font size analysis
    font_sizes = defaultdict(int)
    for block in text_blocks:
        font_sizes[block["size"]] += 1
    avg_size = sum(size * count for size, count in font_sizes.items()) / sum(font_sizes.values())

    # Step 4: Detect potential headings
    def is_potential_heading(block):
        text = block["text"]
        size = block["size"]
        flags = block["flags"]
        score = 0

        # Font size
        if size > avg_size * 1.2:
            score += 3
        elif size > avg_size * 1.1:
            score += 2
        elif size > avg_size:
            score += 1

        

        # Numbered formats
        if re.match(r'^\d+(\.\d+)+\s+\w+', text):
            score -= 5

        elif re.match(r'^Chapter\s+\d+', text, re.IGNORECASE):
            score += 4
        elif re.match(r'^[IVXLCDM]+\.\s+', text):
            score += 3

        # Format heuristics
        if text.isupper() and 3 <= len(text) <= 50:
            score += 2
        if len(text.split()) <= 8 and not text.endswith('.'):
            score += 1
        if len(text) <= 100:
            score += 1

        # Filter out common non-headings
        lower = text.lower()
        false_patterns = [
            'figure', 'table', 'chart', 'image', 'appendix', 'references', 'index',
            'www.', 'http', 'copyright', 'licensed to', '<null>', 'all rights reserved'
        ]
        if any(word in lower for word in false_patterns):
            score -= 3
        if re.match(r'^\d+(\.\d+)*\.?$', text):
            score -= 5
        if len(text) > 200:
            score -= 3

        # Extra citation/reference filters
        citation_patterns = [
        r'\(\d{4}\)',                                # (1995)
        r'\d{4}[:\-]\s*\d+(-\d+)?',                  # 1995: 273 or 1995-273
        r'\bvol\.?\s*\d+\b',                         # vol. 20
        r'\bno\.?\s*\d+\b',                          # no. 3
        r'\bpp?\.?\s*\d+(-\d+)?\b',                  # p. 23 or pp. 273-297
        r'\b[A-Z]\.\s*[A-Z]\.',                      # A. M.
        r'\b\d+\s*\(\d{4}\)',                        # 59 (1950)
        r'“[^”]{5,}”',                               # “Quoted title”
        r'"[^"]{5,}"',                               # "Quoted title"
        r'\b[A-Z][a-z]+,\s*[A-Z]\.([A-Z]\.)?',       # Last, F. or Last, F.M.
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b',       # Full name (e.g., Vladimir Vapnik, Alexey Chervonenkis)
        r'\b[A-Z][a-z]+\s+[A-Z]\.',                  # First Last initials (e.g., Alexey C.)
        r'\bIn\s+Proceedings\b.*?\d{4}',             # In Proceedings ... 2020
        r'\(\d{4}\):\s*\d+(-\d+)?',                  # (1995): 273–297
        r'\[\d+\]',                                  # [1], [23]
        r'(?<!\d)\d{4}(?!\d)',                       # Standalone 4-digit year, avoids matching 12345
    ]
        citation_hits = 0
        for pattern in citation_patterns:
            if re.search(pattern, text):
                citation_hits += 1
        if citation_hits >= 2:
            score -= 6
        elif citation_hits == 1 and len(text) > 50:
            score -= 4
                # Reject lines that are just digits (e.g., "0 1", "2 3", etc.)
        digit_words = sum(1 for w in text.split() if w.isdigit())
        if digit_words >= 2 and digit_words == len(text.split()):
            return False

        return score >= 4

    # Step 5: Collect and sort headings
    headings = [block for block in text_blocks if is_potential_heading(block)]
    headings.sort(key=lambda x: (x["page"], x["bbox"][1]))

    # Step 6: Assign levels
    def determine_level(heading, all_headings):
        text = heading["text"]
        if re.match(r'^\d+\.\d+\.\d+', text):
            return "H3"
        elif re.match(r'^\d+\.\d+', text):
            return "H2"
        elif re.match(r'^\d+\.', text):
            return "H1"
        elif re.match(r'^Chapter\s+\d+', text, re.IGNORECASE):
            return "H1"
        elif re.match(r'^[IVXLCDM]+\.', text):
            return "H1"

        sizes = sorted(set(h["size"] for h in all_headings), reverse=True)
        if heading["size"] == sizes[0]:
            return "H1"
        elif heading["size"] == sizes[1]:
            return "H2"
        elif len(sizes) > 2 and heading["size"] == sizes[2]:
            return "H3"
        else:
            return "H2"

    # Step 7: Build outline
        # Step 7–9: Group by title sections (like CHAPTER 1, PART I, etc.)
    sections = []
    current_section = {
        "title": "Untitled Section",
        "outline": []
    }

    def is_new_section(heading_text):
        return bool(re.match(r'^(Chapter|CHAPTER|Part|PART|Section|SECTION)\s+\w+', heading_text))

    section_map = {}  # Map section title → section object

    for h in headings:
        level = determine_level(h, headings)
        text = h["text"]
        page = h["page"]

        # Use section title if matched, else default
        if is_new_section(text):
            current_title = text
            continue  # Skip adding CHAPTER X itself to outline

        # Use last seen chapter as current_title, else default
        section_title = current_title if 'current_title' in locals() else "Untitled Section"

        if section_title not in section_map:
            section_map[section_title] = {
                "title": section_title,
                "outline": []
            }

        section_map[section_title]["outline"].append({
            "level": level,
            "text": text,
            "page": page
        })

    sections = list(section_map.values())



    if current_section["outline"]:
        sections.append(current_section)

    return {
        "document_title": sections[0]["title"] if sections else "Untitled Document",
        "sections": sections
    }


def process_all_pdfs(input_dir, output_dir):
    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' does not exist.")
        return

    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"No PDF files found in '{input_dir}'")
        return

    print(f"Processing {len(pdf_files)} PDF files...")
    for filename in pdf_files:
        try:
            print(f"Processing: {filename}")
            pdf_path = os.path.join(input_dir, filename)
            result = extract_outline(pdf_path)

            json_filename = filename.replace(".pdf", ".json")
            json_path = os.path.join(output_dir, json_filename)

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"  → Saved outline to: {json_filename}")
            total_headings = sum(len(section["outline"]) for section in result["sections"])
            print(f"  → Found {total_headings} headings in {len(result['sections'])} sections")

        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    input_dir = r"E:\\ELC\\Adobe_Team_while-weTry-\\Part_1A\\input"
    output_dir = r"E:\\ELC\\Adobe_Team_while-weTry-\\Part_1A\\output"

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    print("PDF Outline Extractor")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)

    process_all_pdfs(input_dir, output_dir)