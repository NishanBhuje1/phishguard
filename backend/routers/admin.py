from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.scan import Scan
from models.user import User
from services.auth_service import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_admin(current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


@router.get("/scans")
def admin_scans(
    _=Depends(_require_admin),
    db: Session = Depends(get_db),
):
    scans = db.query(Scan).order_by(Scan.scanned_at.desc()).all()
    return [
        {
            "id": s.id,
            "user_id": s.user_id,
            "url_hash": s.url_hash,
            "verdict": s.verdict,
            "confidence": s.confidence,
            "ip_hash": s.ip_hash,
            "scanned_at": s.scanned_at.isoformat() if s.scanned_at else None,
        }
        for s in scans
    ]


@router.get("/users")
def admin_users(
    _=Depends(_require_admin),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]
