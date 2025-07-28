# Use a minimal Python base image with amd64 architecture
FROM --platform=linux/amd64 python:3.10-slim

# Set work directory inside container
WORKDIR /app

# Copy the local script into container
COPY Step1_PDFExtract.py .

# Install only what's needed
RUN pip install --no-cache-dir PyMuPDF

# Make input and output directories inside the container
RUN mkdir input output

# Run the script when the container starts
CMD ["python", "Step1_PDFExtract.py"]
