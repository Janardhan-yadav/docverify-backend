from fastapi import FastAPI, File, UploadFile, HTTPException, Form
import shutil
from utils.extractor import extract_text_from_file, extract_entities_from_text
import json
from validators import hall_ticket, rank_card, allotment_order, tenth_memo, caste_certificate, income_certificate

app = FastAPI()

# Mapping of document types to their required form fields and validators
DOCUMENT_FIELDS = {
    "hall_ticket": ["hall_ticket_number", "candidate_name", "father_name", "registration_number", "category"],
    "rank_card": ["name", "father_name", "hall_ticket_no", "category", "total_marks", "rank"],
    "allotment_order": ["name", "father_name", "hall_ticket_no", "category", "branch"],
    "tenth_memo": ["name", "father_name", "roll_no", "school_name", "gpa"],
    "caste_certificate": ["name", "father_name", "application_no", "caste"],
    "income_certificate": ["name", "father_name", "application_no", "date"]
}

VALIDATORS = {
    "hall_ticket": hall_ticket.validate,
    "rank_card": rank_card.validate,
    "allotment_order": allotment_order.validate,
    "tenth_memo": tenth_memo.validate,
    "caste_certificate": caste_certificate.validate,
    "income_certificate": income_certificate.validate
}

@app.post("/upload/")
async def upload_document(
    document_type: str = Form(...),
    form_data: str = Form(...),
    file: UploadFile = File(...)
):
    # Parse form data
    try:
        form_data_dict = json.loads(form_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid form data: must be a valid JSON string")

    # Validate that all required fields are present
    required_fields = DOCUMENT_FIELDS.get(document_type)
    if not required_fields:
        raise HTTPException(status_code=400, detail=f"Invalid document type: {document_type}")
    
    missing_fields = [field for field in required_fields if field not in form_data_dict]
    if missing_fields:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing_fields)}")

    # Define file location
    file_location = f"uploads/{file.filename}"
    
    # Save the uploaded file to the server
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract text from the uploaded document using EasyOCR
    extracted_text = extract_text_from_file(file_location)
    
    # Extract entities from the text
    extracted_data = extract_entities_from_text(extracted_text)

    # Route to the appropriate validator
    validator = VALIDATORS.get(document_type)
    if not validator:
        raise HTTPException(status_code=400, detail=f"No validator found for document type: {document_type}")

    # Validate form data against extracted data
    validation_result = validator(form_data_dict, extracted_data, extracted_text)

    # Check if all fields are valid
    all_valid = all(validation_result[field]["is_valid"] for field in validation_result)
    status = "Validation Successful" if all_valid else "Validation Failed"

    return {
        "document_type": document_type,
        "filename": file.filename,
        "extracted_text": extracted_text,
        "extracted_entities": extracted_data,
        "validation_result": validation_result,
        "status": status
    }