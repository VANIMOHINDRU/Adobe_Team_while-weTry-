import fitz  # PyMuPDF
import os
import json
from collections import defaultdict

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    font_sizes = defaultdict(int)
    blocks = []

    # Step 1: Gather font sizes and positions
    for page_num, page in enumerate(doc, start=1):
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        size = round(span["size"], 1)
                        font_sizes[size] += 1
                        blocks.append({
                            "text": span["text"].strip(),
                            "size": size,
                            "page": page_num,
                            "flags": span["flags"]
                        })

    # Step 2: Determine title and heading levels
    sorted_sizes = sorted(font_sizes.items(), key=lambda x: -x[0])
    size_to_level = {}
    
    if sorted_sizes:
        size_to_level[sorted_sizes[0][0]] = "Title"
    if len(sorted_sizes) > 1:
        size_to_level[sorted_sizes[1][0]] = "H1"
    if len(sorted_sizes) > 2:
        size_to_level[sorted_sizes[2][0]] = "H2"
    if len(sorted_sizes) > 3:
        size_to_level[sorted_sizes[3][0]] = "H3"

    title = None
    outline = []

    for b in blocks:
        level = size_to_level.get(b["size"])
        if level == "Title" and not title:
            title = b["text"]
        elif level in ["H1", "H2", "H3"]:
            outline.append({
                "level": level,
                "text": b["text"],
                "page": b["page"]
            })

    return {
        "title": title or "Untitled Document",
        "outline": outline
    }

# Batch process
def process_all_pdfs(input_dir, output_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            result = extract_outline(pdf_path)
            json_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Use current directory for input/output, or set as needed
    input_dir = os.path.join(os.getcwd(), "input")
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(input_dir, exist_ok=True)   # <-- Add this line
    os.makedirs(output_dir, exist_ok=True)
    process_all_pdfs(input_dir, output_dir)
