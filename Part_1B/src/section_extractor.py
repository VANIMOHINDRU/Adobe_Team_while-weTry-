import fitz  # PyMuPDF
import os
import re

def extract_relevant_sections(folder_path, persona, job):
    keyword_set = {k.lower().strip() for k in job.get("keywords", [])}
    extracted = []

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(".pdf"):
            continue

        file_path = os.path.join(folder_path, filename)
        seen_titles = set()  # To avoid duplicates within a doc

        try:
            doc = fitz.open(file_path)

            for page_num in range(len(doc)):
                page = doc[page_num]
                blocks = page.get_text("dict")["blocks"]

                for block in blocks:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()

                            if not text or len(text.split()) > 15:
                                continue  # Skip overly long lines

                            # Heuristic for heading-like lines
                            is_heading = (
                                span["size"] > 12 or
                                (text == text.upper() and text.lower() != text) or  # true uppercase check
                                re.match(r"^\d+(\.\d+)*\s", text)  # numbered headings like "1. ", "2.3 "
                            )


                            if is_heading:
                                text_lc = text.lower()

                                if text_lc in seen_titles:
                                    continue  # avoid duplicate headings

                                if any(k in text_lc for k in keyword_set):
                                    extracted.append({
                                        "document": filename,
                                        "page": page_num + 1,
                                        "section_title": text,
                                        "importance_rank": 0  # Will assign later
                                    })
                                    seen_titles.add(text_lc)

            doc.close()
        except Exception as e:
            print(f"⚠️ Error processing {filename}: {e}")

    # Assign importance based on order
    for i, section in enumerate(extracted):
        section["importance_rank"] = i + 1

    return extracted
