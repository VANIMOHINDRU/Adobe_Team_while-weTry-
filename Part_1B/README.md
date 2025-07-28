# PDF Insight Extractor

This project extracts key insights from PDF documents by analyzing section headings and corresponding content based on a given persona and job-to-be-done. It is designed to assist downstream systems like LLMs or recommender engines in consuming structured outputs.

---

## Overview

Given:
- A set of PDFs
- A user persona (JSON)
- A job-to-be-done (text)

The system:
1. Extracts document metadata
2. Identifies relevant headings and sections
3. Analyzes sub-sections to refine useful content
4. Outputs structured JSON containing all results

---

##  Folder Structure

```

Part_1B/
│
├── main.py                  # Main entry point
├── Dockerfile               # Containerization file
├── requirements.txt         # Python dependencies
├── approach_explanation.md  # This content (merged here)
│
├── sample_input/
│ ├── input_pdfs/
│ │ └── A_Framework_for_Ethical_AI_at_the_UN.pdf
│ ├── sample_persona.json
│ └── job_to_be_done.txt
│
├── sample_output/
│ └── output.json
│
├── src/
│ ├── metadata_extractor.py
│ ├── persona_parser.py
│ ├── section_extractor.py
│ ├── subsection_analyser.py
│ └── job_parser.py

```
---

##  Methodology

### 1. Metadata Extraction

The pipeline begins by:
- Collecting all PDF names
- Parsing the persona JSON (e.g., role, field)
- Reading job-to-be-done text
- Adding a processing timestamp

This provides contextual metadata needed for downstream filtering.

### 2. Section Extraction

Uses PyMuPDF to:
- Parse text blocks per page
- Identify headings based on font size, style (bold/caps), and layout
- Merge multi-line headings if they share font size and are visually continuous
- Store heading positions for extracting nearby content

### 3. Sub-section Analysis

- Locates text under each heading (up to 2–3 pages ahead)
- Extracts only content until the next heading
- Filters based on relevance to the persona and job
- Adds refined text to the output

### 4. Output Structuring

Final output is saved in JSON format with three sections:
- metadata
- extracted_sections
- sub_section_analysis

---

##  Running Locally via Docker

### Step 1: Build Docker Image

Ensure you're in the root directory of the project:

```bash
docker build -t pdf-analyser .
```

## Step 2: Run the Container

```bash 
docker run --rm -v "$(pwd)":/app pdf-analyser

```
This mounts your local folder to the Docker container and runs the analysis. The output will be written to:

```bash
outputs/output.json

```
The JSON contains three top-level keys:

1. metadata  
   General information about the input documents and task context.

2. extracted_sections  
   Key headings and content segments from the PDF relevant to the persona and job.

3. sub_section_analysis  
   Further-refined and filtered sub-sections with contextually important text for the user.

---

## 🧾 Example Output

Here’s a representative structure of output.json:

```json
{
  "metadata": {
    "input_documents": [
      "A_Framework_for_Ethical_AI_at_the_UN.pdf"
    ],
    "persona": {
      "role": "UN Policy Maker",
      "field": "AI Ethics"
    },
    "job_to_be_done": "Identify frameworks to guide ethical deployment of AI at scale in public sector",
    "timestamp": "2025-07-28 17:45:00"
  },
  "extracted_sections": [
    {
      "document": "A_Framework_for_Ethical_AI_at_the_UN.pdf",
      "section_title": "INTRODUCTION",
      "page": 1,
      "content": "This paper introduces the challenges and opportunities of ethical AI in global governance..."
    },
    {
      "document": "A_Framework_for_Ethical_AI_at_the_UN.pdf",
      "section_title": "DEFINING ETHICAL AI",
      "page": 2,
      "content": "Ethical AI refers to principles such as transparency, accountability, fairness..."
    }
  ],
  "sub_section_analysis": [
    {
      "document": "A_Framework_for_Ethical_AI_at_the_UN.pdf",
      "section_title": "DEFINING ETHICAL AI",
      "page": 2,
      "refined_text": "For UN policymakers, ethical AI implies establishing institutional oversight, equity-focused deployment strategies, and legal interoperability across jurisdictions..."
    },
    {
      "document": "A_Framework_for_Ethical_AI_at_the_UN.pdf",
      "section_title": "FRAMEWORK APPLICATION IN THE PUBLIC SECTOR",
      "page": 5,
      "refined_text": "The framework aligns well with public sector mandates—focusing on inclusive AI design, citizen engagement, and policy adaptation for evolving technologies..."
    }
  ]
}
```

## Author
Team while(WeTry)  
Adobe India Hackathon 2025 Submission