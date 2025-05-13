from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserDisplay(UserBase):
    id: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True # Pydantic V1 style, for Pydantic V2 use from_attributes = True
        # from_attributes = True # For Pydantic V2

# Document Schemas
class DocumentBase(BaseModel):
    doc_type: str

class DocumentCreate(DocumentBase):
    # File will be handled via UploadFile
    pass

class DocumentDisplay(DocumentBase):
    id: int
    user_id: int
    file_path: str
    hash: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True
        # from_attributes = True

# Validation Schemas
class ValidationRequestData(BaseModel):
    name: Optional[str] = None
    father_name: Optional[str] = None
    roll_no: Optional[str] = None
    school_name: Optional[str] = None
    gpa: Optional[str] = None
    student_name: Optional[str] = None # Alias for name for some docs
    exam_date: Optional[str] = None
    exam_center: Optional[str] = None
    candidate_name: Optional[str] = None # Alias for name
    rank: Optional[str] = None
    score: Optional[str] = None
    exam_name: Optional[str] = None
    allotted_college: Optional[str] = None
    course: Optional[str] = None
    allotment_date: Optional[str] = None
    applicant_name: Optional[str] = None # Alias for name
    annual_income: Optional[str] = None
    certificate_number: Optional[str] = None
    caste_category: Optional[str] = None
    issuing_authority: Optional[str] = None

class ValidateDocumentRequest(BaseModel):
    doc_type: str
    form_data: Dict[str, Any]

class FieldValidationResult(BaseModel):
    form_value: Optional[str] = None
    extracted_value: Optional[str] = None
    is_valid: bool

class ValidationResponse(BaseModel):
    status: str
    validation_result: Dict[str, FieldValidationResult]
    document_id: Optional[int] = None # Include document ID in response

# Audit Log Schemas
class AuditLogDisplay(BaseModel):
    id: int
    user_id: Optional[int] = None
    document_id: Optional[int] = None
    action: str
    timestamp: datetime.datetime

    class Config:
        orm_mode = True
        # from_attributes = True

