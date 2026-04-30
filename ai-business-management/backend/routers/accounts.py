"""
Account management router — upload/manage per-user service accounts.
"""
import json
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from database import get_db
from models.user_account import UserAccount
from services import crypto_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/accounts", tags=["User Accounts"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class UploadSARequest(BaseModel):
    uid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    service_account_json: dict  # The raw SA JSON object


class UpdateSheetURLRequest(BaseModel):
    uid: str
    sheet_url: str


class AccountStatusResponse(BaseModel):
    uid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    sa_configured: bool
    sa_project_id: Optional[str] = None
    sa_client_email: Optional[str] = None
    sheet_url: Optional[str] = None


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/upload-sa", summary="Upload & encrypt a service account JSON")
async def upload_service_account(req: UploadSARequest, db: Session = Depends(get_db)):
    """
    Accepts a Google Cloud service account JSON, encrypts it,
    and stores it in MySQL tied to the user's Firebase UID.
    """
    # Validate SA structure
    sa = req.service_account_json
    if sa.get("type") != "service_account":
        raise HTTPException(status_code=400, detail="Invalid service account JSON: 'type' must be 'service_account'.")
    if not sa.get("private_key") or not sa.get("client_email"):
        raise HTTPException(status_code=400, detail="Invalid service account JSON: missing 'private_key' or 'client_email'.")

    # Encrypt the SA JSON
    sa_plaintext = json.dumps(sa)
    sa_encrypted = crypto_service.encrypt(sa_plaintext)

    # Upsert user account
    account = db.query(UserAccount).filter(UserAccount.firebase_uid == req.uid).first()
    if account:
        account.sa_encrypted = sa_encrypted
        account.email = req.email or account.email
        account.display_name = req.display_name or account.display_name
    else:
        account = UserAccount(
            firebase_uid=req.uid,
            email=req.email,
            display_name=req.display_name,
            sa_encrypted=sa_encrypted,
        )
        db.add(account)

    db.commit()
    logger.info("Service account uploaded for UID=%s (project=%s)", req.uid, sa.get("project_id"))

    return {
        "success": True,
        "message": "Service account uploaded and encrypted successfully.",
        "sa_client_email": sa.get("client_email"),
        "sa_project_id": sa.get("project_id"),
    }


@router.get("/status/{uid}", summary="Check if a user has SA configured", response_model=AccountStatusResponse)
async def get_account_status(uid: str, db: Session = Depends(get_db)):
    """Returns the configuration status for a user's account."""
    account = db.query(UserAccount).filter(UserAccount.firebase_uid == uid).first()

    if not account:
        return AccountStatusResponse(uid=uid, sa_configured=False)

    # Decrypt just enough to show project info (not the private key)
    sa_project_id = None
    sa_client_email = None
    if account.sa_encrypted:
        try:
            sa_json = json.loads(crypto_service.decrypt(account.sa_encrypted))
            sa_project_id = sa_json.get("project_id")
            sa_client_email = sa_json.get("client_email")
        except Exception:
            pass  # Corrupted or key mismatch — still report as configured

    return AccountStatusResponse(
        uid=uid,
        email=account.email,
        display_name=account.display_name,
        sa_configured=account.sa_encrypted is not None,
        sa_project_id=sa_project_id,
        sa_client_email=sa_client_email,
        sheet_url=account.sheet_url,
    )


@router.put("/sheet-url", summary="Save user's Google Sheet URL")
async def update_sheet_url(req: UpdateSheetURLRequest, db: Session = Depends(get_db)):
    """Saves or updates the user's Google Sheet URL in their account."""
    account = db.query(UserAccount).filter(UserAccount.firebase_uid == req.uid).first()
    if not account:
        account = UserAccount(firebase_uid=req.uid, sheet_url=req.sheet_url)
        db.add(account)
    else:
        account.sheet_url = req.sheet_url
    db.commit()

    return {"success": True, "message": "Sheet URL saved."}


@router.delete("/{uid}", summary="Remove user's service account")
async def delete_service_account(uid: str, db: Session = Depends(get_db)):
    """Removes the encrypted SA for a user (revokes backend access to their sheets)."""
    account = db.query(UserAccount).filter(UserAccount.firebase_uid == uid).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found.")

    account.sa_encrypted = None
    db.commit()
    logger.info("Service account removed for UID=%s", uid)

    return {"success": True, "message": "Service account removed."}
