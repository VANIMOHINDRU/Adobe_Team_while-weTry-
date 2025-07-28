from metadata_extractor import extract_metadata
from section_extractor import extract_relevant_sections

# Step 1: Get metadata
metadata = extract_metadata("data/input_pdfs")
persona = metadata["persona"]
job_to_be_done = metadata["job_to_be_done"]

# Step 2: Get relevant sections using section_extractor
folder_path = "data/input_pdfs"
sections = extract_relevant_sections(folder_path, persona, job_to_be_done)

# Step 3: Add to metadata
metadata["extracted_sections"] = sections

# (Optional) Save to JSON
import json
with open("output.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print("✅ Section extraction complete. Results saved to output.json")
