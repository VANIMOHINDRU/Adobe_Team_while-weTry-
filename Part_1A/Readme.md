# Adobe India Hackathon 2025 - Challenge 1A: PDF Processing Solution

## Overview

This repository provides a containerized solution to extract structured JSON data from PDF documents. The task is to automatically parse PDFs and output JSON files conforming to a defined schema. This submission is built for Challenge 1A of the Adobe India Hackathon 2025.

The system:
- Accepts PDFs from the `/app/input` directory
- Outputs structured JSON to `/app/output`
- Is packaged using Docker for AMD64 CPU architecture
- Runs without internet access and within specified performance limits

---

## Approach

The implemented pipeline includes:

1. **PDF Parsing using PyMuPDF (`fitz`)**  
   Each page in the input PDF is scanned to extract individual text blocks along with their positions, font sizes, and attributes.

2. **Heading Detection & Hierarchy Classification**  
   - Text blocks are analyzed for font size and style (bold, font weight) to identify heading candidates.
   - Headings are classified as `H1`, `H2`, or `H3` based on relative font sizes within the document.
   - Multi-line headings are merged intelligently if they share the same font size and alignment.

3. **Numeric Filtering Logic**  
   Headings with leading numeric patterns (e.g., `2.2.11 Introduction`) are **excluded** to focus only on semantic headings. This is done using regex filters that discard lines starting with numbering patterns like: 1.2,2.3.4,3.0.1.5 etc.

4. **Output Format**  
For every input `filename.pdf`, a structured JSON file named `filename.json` is generated in the `output/` folder. This JSON includes:
```json
{
  "Title": "Document Title",
  "Headings": [
    { "type": "H1", "text": "Introduction" },
    { "type": "H2", "text": "System Design" },
    { "type": "H3", "text": "Modules Overview" }
  ]
}
```
---

## Models and Libraries Used

- `PyMuPDF (fitz)` - For layout-aware PDF text extraction
- Standard Python libraries: `re`, `json`, `os`, `pathlib`
- No external ML model used – rule-based lightweight implementation

---

## Docker Instructions

### Build the Image

Make sure you are inside the `Part_1A` directory containing the `Dockerfile`.

```bash
docker build --platform linux/amd64 -t adobe_while_wetry .
```

---

### Run the Container

```bash
docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none adobe_while_wetry
```

- Ensure the `/input` folder contains your PDF files.
- Output JSON files will be saved in the `/output` directory.

---

## Project Structure

```
Part_1A/
├── Dockerfile
├── Step1_PDFExtract.py
├── input/                  # (mounted during Docker run)
│   └── *.pdf
├── output/                 # (Docker writes output here)
├── sample.json             # Example output
└── README.md               # This file
```

---

## Output Specification

- For each `filename.pdf` in the `input/`, a `filename.json` will be generated in `output/`
- The JSON follows the format defined in the schema provided during the challenge
- Only textual (non-numeric) headings are retained
- Multi-line headings with consistent font size and layout are merged

---

## Example Output

For a file named `sample.pdf` placed in the `input/` directory, the following JSON will be generated inside `output/sample.json`:

```json

{
  "document_title": "CHAPTER 1",
  "sections": [
    {
      "title": "CHAPTER 1",
      "outline": [
        {
          "level": "H1",
          "text": "Artificial intelligence, machine learning, and deep learning",
          "page": 1
        },
        {
          "level": "H2",
          "text": "Artificial intelligence",
          "page": 1
        },
        {
          "level": "H2",
          "text": "Machine learning",
          "page": 1
        },
        {
          "level": "H2",
          "text": "Learning representations from data",
          "page": 3
        },
        {
          "level": "H2",
          "text": "The “deep” in deep learning",
          "page": 5
        },
        {
          "level": "H2",
          "text": "What deep learning has achieved so far",
          "page": 8
        },
        {
          "level": "H2",
          "text": "Don’t believe the short-term hype",
          "page": 9
        },
        {
          "level": "H2",
          "text": "The promise of AI",
          "page": 10
        },
        {
          "level": "H1",
          "text": "Before deep learning: a brief history of machine learning",
          "page": 11
        },
        {
          "level": "H2",
          "text": "Probabilistic modeling",
          "page": 11
        },
```

---

## Validation Checklist

- [x] All PDFs in `/app/input` are processed
- [x] Each output JSON file matches the name of its PDF
- [x] JSON structure conforms to the schema
- [x] Processes up to 50 pages in under 10 seconds
- [x] No internet access required during execution
- [x] Docker image size is under 200MB
- [x] Compatible with Linux AMD64 architecture

---

## Testing Strategy

Tested on:
- Academic articles (single-column)
- Multi-column research papers
- Simulated large PDFs (up to 50 pages)

---

## Notes

- The `input/` directory is mounted read-only
- Output is automatically written to `output/`
- No interactive prompts; the container runs autonomously and exits after processing

---

## Author

Team while(WeTry)  
Adobe India Hackathon 2025 Submission

