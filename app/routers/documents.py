from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import shutil
import os
import hashlib
import uuid

from .. import auth, database, schemas, storage # Adjusted import path
from ..models.ner_model import ner_trainer # Placeholder for NER model
from ..models.validation_model import validation_trainer # Placeholder for validation model
# from ..models.data_preparation import prepare_data # For actual data prep if needed here
import easyocr

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(auth.get_current_active_user)]
)

TEMP_UPLOAD_DIR = "/tmp/docverify_uploads"
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

# Initialize EasyOCR Reader
# This can take a moment, so it's good to do it once when the module is loaded
# or manage it as a dependency if it's very heavy.
ocr_reader = easyocr.Reader(["en"])

def get_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

@router.post("/validate", response_model=schemas.ValidationResponse)
async def validate_document_endpoint(
    doc_type: str = Form(...),
    form_data_json: str = Form(...), # Receive form_data as JSON string
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: database.User = Depends(auth.get_current_active_user),
    minio_client = Depends(storage.get_minio_client)
):
    import json
    try:
        form_data = json.loads(form_data_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in form_data")

    # 1. Save uploaded file temporarily
    temp_file_path = os.path.join(TEMP_UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Perform OCR
        ocr_results = ocr_reader.readtext(temp_file_path)
        extracted_text_ocr = " ".join([res[1] for res in ocr_results])
        
        # 3. Use NER model to extract key fields from OCR output
        # This is a placeholder. Actual NER model integration is more complex.
        extracted_fields_ner = ner_trainer.predict_ner(extracted_text_ocr) # Returns a dict

        # 4. Use validation model to compare extracted fields with form data
        validation_results_dict = {}
        # The form_data from the request needs to be parsed against DOC_TYPES_FIELDS
        # For now, we iterate through form_data keys, assuming they are the fields to validate
        relevant_fields_for_doc_type = form_data.keys() # Simplified, should use DOC_TYPES_FIELDS from data_prep

        for field_name in relevant_fields_for_doc_type:
            form_value = str(form_data.get(field_name, ""))
            extracted_value_ner = str(extracted_fields_ner.get(field_name, "")) # Get corresponding NER extracted value
            
            # Placeholder for actual validation model prediction
            is_valid = validation_trainer.predict_validation(extracted_value_ner, form_value)
            
            validation_results_dict[field_name] = schemas.FieldValidationResult(
                form_value=form_value,
                extracted_value=extracted_value_ner,
                is_valid=is_valid
            )

        # 5. Store document securely (encrypt then upload to MinIO)
        # Encryption step is omitted for brevity here but should be implemented
        file_hash = get_file_hash(temp_file_path)
        minio_object_name = f"{current_user.id}/{uuid.uuid4()}_{file.filename}"
        
        storage.create_bucket_if_not_exists(minio_client, storage.MINIO_BUCKET_NAME)
        storage.upload_file_to_minio(minio_client, storage.MINIO_BUCKET_NAME, minio_object_name, temp_file_path)

        # 6. Save document metadata and validation results in PostgreSQL
        db_document = database.Document(
            user_id=current_user.id,
            file_path=minio_object_name, # Store MinIO object name/path
            hash=file_hash,
            doc_type=doc_type
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)

        for field, result in validation_results_dict.items():
            db_validation_result = database.ValidationResult(
                document_id=db_document.id,
                field_name=field,
                form_value=result.form_value,
                extracted_value=result.extracted_value,
                is_valid=result.is_valid
            )
            db.add(db_validation_result)
        db.commit()
        
        # Log audit event
        audit_log = database.AuditLog(user_id=current_user.id, document_id=db_document.id, action=f"validate_document_{doc_type}")
        db.add(audit_log)
        db.commit()

        return schemas.ValidationResponse(
            status="Validation Completed", 
            validation_result=validation_results_dict,
            document_id=db_document.id
        )

    except Exception as e:
        # Log error e
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@router.get("/{document_id}", response_model=schemas.DocumentDisplay)
async def get_document_details(
    document_id: int,
    db: Session = Depends(database.get_db),
    current_user: database.User = Depends(auth.get_current_active_user)
):
    db_document = db.query(database.Document).filter(database.Document.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    if db_document.user_id != current_user.id: # Add admin role check later if needed
        raise HTTPException(status_code=403, detail="Not authorized to access this document")
    
    # Log audit event
    audit_log = database.AuditLog(user_id=current_user.id, document_id=db_document.id, action="get_document_details")
    db.add(audit_log)
    db.commit()
    return db_document

@router.get("/{document_id}/download") # Actual file download, not just metadata
async def download_document_file(
    document_id: int,
    db: Session = Depends(database.get_db),
    current_user: database.User = Depends(auth.get_current_active_user),
    minio_client = Depends(storage.get_minio_client)
):
    db_document = db.query(database.Document).filter(database.Document.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    if db_document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")

    try:
        # Decryption step would be here before returning the file
        presigned_url = storage.get_file_url_from_minio(minio_client, storage.MINIO_BUCKET_NAME, db_document.file_path)
        # Log audit event
        audit_log = database.AuditLog(user_id=current_user.id, document_id=db_document.id, action="download_document_file")
        db.add(audit_log)
        db.commit()
        return {"download_url": presigned_url} # Client can use this URL to download
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve file: {str(e)}")

@router.post("/{document_id}/verify_integrity")
async def verify_document_integrity(
    document_id: int,
    file: UploadFile = File(...), # User re-uploads to verify
    db: Session = Depends(database.get_db),
    current_user: database.User = Depends(auth.get_current_active_user)
):
    db_document = db.query(database.Document).filter(database.Document.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Document not found")
    if db_document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")

    temp_file_path = os.path.join(TEMP_UPLOAD_DIR, f"{uuid.uuid4()}_verify_{file.filename}")
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        current_hash = get_file_hash(temp_file_path)
        
        # Log audit event
        action_detail = "verify_integrity_match" if current_hash == db_document.hash else "verify_integrity_mismatch"
        audit_log = database.AuditLog(user_id=current_user.id, document_id=db_document.id, action=action_detail)
        db.add(audit_log)
        db.commit()

        if current_hash == db_document.hash:
            return {"status": "success", "message": "Document integrity verified. Hashes match."}
        else:
            return {"status": "failure", "message": "Document integrity check failed. Hashes do not match."}
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

