from datetime import datetime, timedelta
import re
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.settings import settings
from app.security.security import verify_password
from app.services.user_service import get_user_by_username
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_token(token: str, credentials_exception, db):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = get_user_by_username(username, db)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception
    

def authenticate_user(username: str, password: str, db):
    user = get_user_by_username(username, db)
    if not user or not verify_password(pwd_context, password, user.hashed_password):
        return False
    return user

def verify_password_service( password: str , hashed_password: str) :
    return verify_password(pwd_context, password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def generate_password_reset_token(email: str):
    expires_delta = timedelta(hours=1)
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": email}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def verify_password_reset_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get('sub')
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def validate_password_strength(password: str):
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")
    if not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one digit")
    if not re.search(r"[\W_]", password):
        errors.append("Password must contain at least one special character")

    if errors:
        raise HTTPException(status_code=400, detail=errors)

def get_user_by_email(email: str, db):
    return db["users"].find_one({"email": email})

def store_password_reset_token(email: str, token: str, db, expires_at: datetime):
    db["password_reset_tokens"].insert_one({
        "email": email,
        "token": token,
        "expires_at": expires_at,
        "used": False
    })

def mark_token_as_used(token: str, db):
    db["password_reset_tokens"].update_one({"token": token}, {"$set": {"used": True}})

def validate_reset_token(token: str, db):
    token_data = db["password_reset_tokens"].find_one({"token": token})
    if not token_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    if token_data["used"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token has already been used")
    if token_data["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token has expired")
    return token_data["email"]
