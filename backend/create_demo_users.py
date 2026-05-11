import sys
sys.path.insert(0, '.')
from database import SessionLocal, init_db
from models.user import User
from services.auth_service import hash_password
import pyotp

init_db()
db = SessionLocal()

accounts = [
    {"email": "demo@phishguard.com", "password": "Demo1234!", "role": "user"},
    {"email": "admin@phishguard.com", "password": "Admin1234!", "role": "admin"},
]

for acc in accounts:
    existing = db.query(User).filter(User.email == acc["email"]).first()
    if existing:
        print(f"Already exists: {acc['email']}")
        continue
    totp_secret = pyotp.random_base32()
    user = User(
        email=acc["email"],
        password_hash=hash_password(acc["password"]),
        totp_secret=totp_secret,
        role=acc["role"]
    )
    db.add(user)
    db.commit()
    totp_uri = f"otpauth://totp/PhishGuard:{acc['email']}?secret={totp_secret}&issuer=PhishGuard"
    print(f"Created: {acc['email']} | Role: {acc['role']}")
    print(f"TOTP Secret: {totp_secret}")
    print(f"TOTP URI: {totp_uri}")
    print()

db.close()
