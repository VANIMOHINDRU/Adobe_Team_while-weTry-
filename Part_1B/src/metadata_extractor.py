import fitz  # PyMuPDF
import os
from datetime import datetime
import pytz
from collections import Counter

def extract_pdf_metadata(folder_path):
    pdf_metadata = []

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Input folder not found: {folder_path}")

    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(folder_path, filename)
            try:
                doc = fitz.open(file_path)

                title = doc.metadata.get("title", "").strip()

                if not title:
                    # Use a smarter fallback: combine lines with same font size at top of page
                    page = doc[0]
                    blocks = page.get_text("dict")["blocks"]

                    spans = []
                    for block in blocks:
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                spans.append({
                                    "text": span.get("text", "").strip(),
                                    "size": span.get("size", 0),
                                    "y": span.get("bbox", [0, 0, 0, 0])[1]
                                })

                    spans = sorted(spans, key=lambda x: x["y"])

                    sizes = [span["size"] for span in spans if span["text"]]
                    if sizes:
                        common_size = Counter(sizes).most_common(1)[0][0]

                        title_lines = []
                        for span in spans:
                            if abs(span["size"] - common_size) < 0.5 and span["text"]:
                                title_lines.append(span["text"])
                            elif title_lines:
                                # Stop once we hit a line with different size after collecting some
                                break

                        title = " ".join(title_lines).strip() if title_lines else "Unknown Title"

                    else:
                        title = "Unknown Title"

                page_count = doc.page_count

                pdf_metadata.append({
                    "filename": filename,
                    "title": title,
                    "page_count": page_count
                })

                doc.close()

            except Exception as e:
                print(f"⚠️ Error reading {filename}: {e}")
    
    return pdf_metadata

def get_processing_timestamp():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).isoformat()
