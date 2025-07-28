import fitz  # PyMuPDF
import os
import re

def extract_subsections(folder_path, extracted_sections):
    subsection_data = []

    for section in extracted_sections:
        filename = section["document"]
        page_number = section["page"]
        heading_text = section["section_title"].strip()
        file_path = os.path.join(folder_path, filename)

        try:
            doc = fitz.open(file_path)
            page = doc[page_number - 1]  # 1-indexed
            blocks = page.get_text("dict")["blocks"]

            heading_found = False
            collecting = False
            refined_lines = []
            heading_size = None

            for block in blocks:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if not text:
                            continue

                        # Use substring match to find heading
                        if not heading_found and heading_text.lower() in text.lower():
                            heading_found = True
                            heading_size = span.get("size", 0)
                            collecting = True
                            continue

                        if collecting:
                            # Stop if next heading detected
                            is_next_heading = (
                                span.get("size", 0) >= heading_size and
                                (
                                    (text == text.upper() and text.lower() != text) or
                                    re.match(r"^\d+(\.\d+)*\s", text)
                                )
                            )
                            if is_next_heading:
                                collecting = False
                                break

                            refined_lines.append(text)

                if not collecting and heading_found:
                    break

            if not heading_found:
                print(f"⚠️ Heading not found in {filename} on page {page_number}: '{heading_text}'")

            refined_text = " ".join(refined_lines).strip()

            subsection_data.append({
                "document": filename,
                "section_title": heading_text,
                "refined_text": refined_text,
                "page": page_number
            })

            doc.close()

        except Exception as e:
            print(f"⚠️ Error processing section in {filename}: {e}")

    return subsection_data
