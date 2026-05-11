from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from middleware.rate_limiter import limiter
from models.scan import Scan
from services.auth_service import get_current_user
from services.logger import log_scan
from services.ml_classifier import classify_url
from services.url_analyzer import extract_features

router = APIRouter()


class ScanRequest(BaseModel):
    url: str


def _validate_url(url: str) -> None:
    if not url or not url.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL cannot be empty")
    if len(url) > 2048:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="URL too long")
    if not (url.startswith("http://") or url.startswith("https://")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL format")


@router.post("/scan")
@limiter.limit("10/minute")
async def scan_url(
    request: Request,
    body: ScanRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _validate_url(body.url)

    features = extract_features(body.url)
    result = classify_url(features)

    ip = request.client.host or "unknown"
    log_scan(
        user_id=current_user.id,
        url=body.url,
        verdict=result["verdict"],
        confidence=result["confidence"],
        ip=ip,
    )

    return {
        "verdict": result["verdict"],
        "confidence": result["confidence"],
        "phishtank_match": features["phishtank_match"],
        "features": features,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/scan/history")
def scan_history(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.scanned_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "url_hash": s.url_hash,
            "verdict": s.verdict,
            "confidence": s.confidence,
            "scanned_at": s.scanned_at.isoformat() if s.scanned_at else None,
        }
        for s in scans
    ]
