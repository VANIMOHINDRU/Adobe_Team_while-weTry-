from src.metadata_extractor import extract_pdf_metadata, get_processing_timestamp
from src.persona_parser import parse_persona
from src.section_extractor import extract_relevant_sections
from src.job_parser import parse_job
from src.subsection_analyser import extract_subsections
import json
import os

folder = "data/input_pdfs"
persona_path = "data/sample_persona.json"
job_path = "data/job_to_be_done.txt"

# Step 1: Extract metadata
output = {
    "metadata": {
        "input_documents": extract_pdf_metadata(folder),
        "persona": parse_persona(persona_path),
        "job_to_be_done": parse_job(job_path),
        "timestamp": get_processing_timestamp()
    }
}

# Step 2: Extract relevant sections
output["extracted_sections"] = extract_relevant_sections(
    folder_path=folder,
    persona=output["metadata"]["persona"],
    job=output["metadata"]["job_to_be_done"]
)

# Step 3: Extract sub-section analysis
output["sub_section_analysis"] = extract_subsections(
    folder_path=folder,
    extracted_sections=output["extracted_sections"]
)

# Ensure output folder exists
os.makedirs("outputs", exist_ok=True)

# Save to outputs/output.json
with open("outputs/output.json", "w") as f:
    json.dump(output, f, indent=2)
