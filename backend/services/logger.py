import hashlib
from database import SessionLocal
from models.scan import Scan


def hash_value(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def log_scan(user_id: int, url: str, verdict: str, confidence: float, ip: str):
    db = SessionLocal()
    try:
        scan = Scan(
            user_id=user_id,
            url_hash=hash_value(url),
            verdict=verdict,
            confidence=confidence,
            ip_hash=hash_value(ip),
        )
        db.add(scan)
        db.commit()
    finally:
        db.close()
