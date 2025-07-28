# Approach Explanation

## Overview

This project processes PDF documents to extract structured insights by identifying key sections and analyzing subsections relevant to a given persona and job description. The solution is modular, supports multiple documents, and is Dockerized for portability and reproducibility.

## Methodology

1. Metadata Extraction
   The process begins by scanning the input folder and capturing all PDF filenames, a timestamp, and associated metadata like the persona (user profile) and job-to-be-done text. This step ensures contextual alignment for downstream filtering.

2. Section Extraction
   The `section_extractor.py` module parses all pages using PyMuPDF. It clusters headings based on font size, boldness, and structural patterns (like Title Case, All Caps, or section numbers like "1.1"). Consecutive lines with the same font size and layout are merged to reconstruct multiline headings.

3. Sub-section Analysis
   Each section heading identified is passed to the `subsection_analyser.py`, which:
   - Scans pages near the heading’s location
   - Extracts refined text between this heading and the next
   - Validates relevance based on persona and job keywords
   - Limits extraction to 2–3 pages ahead to ensure scope consistency

4. Output Generation
   The processed output is written to JSON, containing metadata, all extracted sections, and refined subsection text for analysis. The output structure supports direct parsing by downstream LLMs or recommender systems.

## Key Design Decisions

- PyMuPDF is used due to its precision and speed in extracting layout-aware information from PDFs.
- Multi-line heading merging is crucial to handle wrapped section titles split across lines.
- Subsection boundaries are dynamically determined based on heading position and font hierarchy.
- Docker is used to encapsulate the environment and ensure the tool runs identically across systems.
- Volume mounting via $(pwd):/app ensures seamless integration with local directories without changing file paths in the code.

## Testing

We provide sample input and output files to verify pipeline correctness. The command `docker run --rm -v "$(pwd)":/app pdf-analyser` executes the entire flow from PDF to structured output JSON.

This modular pipeline can be extended to include summarization, tagging, or semantic clustering for further insights.
