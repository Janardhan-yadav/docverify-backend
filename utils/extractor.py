# utils/extractor.py

import easyocr
import os
import pdfplumber
import re

# Initialize the EasyOCR reader with the required language(s)
reader = easyocr.Reader(['en'])  # Adjust the language if necessary, e.g., 'hi' for Hindi

def extract_text_from_file(file_path: str) -> str:
    """Determine the file type and extract text accordingly."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.jpg', '.jpeg', '.png']:
        return extract_text_from_image(file_path)
    else:
        return "Unsupported file type."

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF by converting each page to an image."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_image = page.to_image(resolution=300)  # High-resolution image
            img_path = "temp_page.png"
            page_image.save(img_path, format="PNG")  # Save page image temporarily
            text += extract_text_from_image(img_path) + "\n"  # Extract text from image
            os.remove(img_path)  # Clean up temporary image file
    return text.strip()

def extract_text_from_image(file_path: str) -> str:
    """Extract text from image using EasyOCR."""
    results = reader.readtext(file_path, detail=0)  # Only text without bounding box details
    return "\n".join(results).strip()  # Return extracted text as a single string

def extract_entities_from_text(text: str) -> dict:
    """Extract key entities such as names, dates, and amounts from the extracted text."""
    entities = {
        "names": [],
        "dates": [],
        "amounts": [],
        "addresses": [],
        "alphanumeric": []  # Added for extracting alphanumeric strings (e.g., roll numbers, hall ticket numbers)
    }

    # Regex pattern for extracting names (simple version - First Last name format)
    name_pattern = r"[A-Z]+ [A-Z]+"  # Example: John Doe
    entities["names"] = re.findall(name_pattern, text)

    # Regex pattern for extracting dates (simple format like dd/mm/yyyy or mm/dd/yyyy)
    date_pattern = r"\b(\d{2}/\d{2}/\d{4})\b"  # Example: 12/12/2025 or 12/31/2025
    entities["dates"] = re.findall(date_pattern, text)

    # Regex pattern for extracting monetary amounts (simple version)
    amount_pattern = r"\$\d+(?:,\d{3})*(?:\.\d{2})?"  # Example: $1,234.56
    entities["amounts"] = re.findall(amount_pattern, text)

    # Regex pattern for extracting simple addresses (looking for street-like patterns)
    address_pattern = r"\d+\s[A-Za-z]+\s[A-Za-z]+(?:\s[A-Za-z]+)*"  # Example: 123 Main Street
    entities["addresses"] = re.findall(address_pattern, text)

    # Regex pattern for extracting alphanumeric strings (e.g., roll numbers, hall ticket numbers)
    # Regex pattern for extracting alphanumeric roll numbers or hall ticket numbers
    alphanumeric_pattern = r"\b[A-Z0-9]{8,}\b"
    entities["alphanumeric"] = re.findall(alphanumeric_pattern, text.upper())


    return entities
