from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import auth, database, schemas # Adjusted import path

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_current_active_user)]
)

@router.get("/logs", response_model=List[schemas.AuditLogDisplay])
async def get_audit_logs(
    user_id: Optional[int] = Query(None, description="Filter logs by user ID"),
    document_id: Optional[int] = Query(None, description="Filter logs by document ID"),
    db: Session = Depends(database.get_db),
    current_user: database.User = Depends(auth.get_current_active_user)
):
    # Basic authorization: users can only see their own logs unless they are an admin (not implemented yet)
    # For now, let's assume an admin role would bypass this or have broader query capabilities.
    # If a non-admin user tries to query for another user_id, it should be restricted.
    # This is a simplified version. A real system would have more robust role-based access control.

    query = db.query(database.AuditLog)

    # If a specific user_id is requested, ensure the current user is that user or an admin
    if user_id is not None:
        if user_id != current_user.id: # and not current_user.is_admin: # Add admin check later
            raise HTTPException(status_code=403, detail="Not authorized to view logs for this user")
        query = query.filter(database.AuditLog.user_id == user_id)
    else:
        # If no specific user_id is given, non-admins should only see their own logs.
        # Admins could see all if user_id is None.
        # For now, default to current user's logs if no user_id is specified by a non-admin.
        query = query.filter(database.AuditLog.user_id == current_user.id)

    if document_id is not None:
        # Check if the current user has access to this document's logs
        # This might involve checking if the document belongs to the user
        doc = db.query(database.Document).filter(database.Document.id == document_id).first()
        if not doc or doc.user_id != current_user.id: # and not current_user.is_admin:
             raise HTTPException(status_code=403, detail="Not authorized to view logs for this document")
        query = query.filter(database.AuditLog.document_id == document_id)
    
    logs = query.order_by(database.AuditLog.timestamp.desc()).all()
    return logs

