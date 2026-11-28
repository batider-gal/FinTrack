"""Local authentication: Argon2 passwords and revocable signed JWT sessions."""
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Annotated
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User, Category, AuthSession

DEMO_EMAIL = 'demo@fintrack.invalid'
router = APIRouter(prefix='/api/auth', tags=['Authentication'])
# Local-only key: restarting the server invalidates existing tokens.
KEY = secrets.token_bytes(32)
TTL = 3600
hasher = PasswordHasher()
bearer = HTTPBearer(auto_error=False)

def get_db():
    with SessionLocal() as db:
        yield db

DB = Annotated[Session, Depends(get_db)]

class Credentials(BaseModel):
    model_config = ConfigDict(extra='forbid')
    email: str = Field(max_length=254)
    password: str = Field(min_length=12, max_length=128)

    @field_validator('email')
    @classmethod
    def normalize_email(cls, value):
        value = value.strip().lower()
        parts = value.split('@')
        if len(parts) != 2 or not all(parts) or '.' not in parts[1] or any(c.isspace() for c in value):
            raise ValueError('Enter a valid email address')
        return value

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str

class TokenRead(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    expires_in: int = TTL

def unauthorized():
    return HTTPException(401, 'Invalid or expired credentials', headers={'WWW-Authenticate': 'Bearer'})

def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()

def current_session(db: DB, credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]):
    if credentials is None:
        raise unauthorized()
    token = credentials.credentials
    try:
        claims = jwt.decode(token, KEY, algorithms=['HS256'], issuer='fintrack', audience='fintrack-api', options={'require': ['sub', 'exp', 'iat', 'jti']})
        uid = int(claims['sub'])
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise unauthorized() from None
    session = db.get(AuthSession, digest(token))
    if session is None or session.user_id != uid or session.expires_at <= int(datetime.now(timezone.utc).timestamp()):
        raise unauthorized()
    return session

def current_user_id(session: Annotated[AuthSession, Depends(current_session)]):
    return session.user_id

CurrentUser = Annotated[int, Depends(current_user_id)]

@router.post('/register', response_model=UserRead, status_code=201)
def register(payload: Credentials, db: DB):
    if payload.email == DEMO_EMAIL:
        raise HTTPException(409, 'Email unavailable')
    user = User(email=payload.email, password_hash=hasher.hash(payload.password))
    db.add(user)
    try:
        db.flush()
        db.add_all([Category(user_id=user.id, name=name, kind=kind) for kind, name in [('income','Salary'),('income','Other income'),('expense','Food'),('expense','Housing'),('expense','Transport'),('expense','Other expenses')]])
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Email unavailable') from None
    db.refresh(user)
    return user

@router.post('/login', response_model=TokenRead)
def login(payload: Credentials, db: DB):
    user = db.scalar(select(User).where(User.email == payload.email))
    if user is None or user.email == DEMO_EMAIL:
        raise unauthorized()
    try:
        hasher.verify(user.password_hash, payload.password)
    except (VerificationError, InvalidHashError):
        raise unauthorized() from None
    now = int(datetime.now(timezone.utc).timestamp())
    token = jwt.encode({'sub': str(user.id), 'iat': now, 'exp': now+TTL, 'jti': secrets.token_hex(16), 'iss':'fintrack', 'aud':'fintrack-api'}, KEY, algorithm='HS256')
    db.execute(delete(AuthSession).where(AuthSession.expires_at <= now))
    db.add(AuthSession(token_hash=digest(token), user_id=user.id, expires_at=now+TTL))
    db.commit()
    return TokenRead(access_token=token)

@router.get('/me', response_model=UserRead)
def me(db: DB, uid: CurrentUser):
    return db.get(User, uid)

@router.post('/logout', status_code=204)
def logout(db: DB, session: Annotated[AuthSession, Depends(current_session)]):
    db.delete(session)
    db.commit()
    return Response(status_code=204)
