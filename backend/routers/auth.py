from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import pyotp

from database import get_db
from middleware.rate_limiter import limiter
from models.user import User
from services.auth_service import (
    hash_password,
    verify_password,
    create_jwt,
    create_temp_jwt,
    decode_jwt,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Verify2FARequest(BaseModel):
    temp_token: str
    code: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    totp_secret = pyotp.random_base32()
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        totp_secret=totp_secret,
        role="user",
    )
    db.add(user)
    db.commit()

    totp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
        name=body.email, issuer_name="PhishGuard"
    )
    return {
        "message": "registered",
        "email": body.email,
        "totp_secret": totp_secret,
        "totp_uri": totp_uri,
    }


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    temp_token = create_temp_jwt(user.id)
    return {"temp_token": temp_token, "token_type": "bearer"}


@router.post("/verify-2fa")
@limiter.limit("5/minute")
async def verify_2fa(request: Request, body: Verify2FARequest, db: Session = Depends(get_db)):
    payload = decode_jwt(body.temp_token)
    if payload.get("type") != "temp":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if not pyotp.TOTP(user.totp_secret).verify(body.code):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid TOTP code")

    access_token = create_jwt(user.id, user.role)
    return {"access_token": access_token, "token_type": "bearer"}
