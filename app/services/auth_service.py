from datetime import datetime, timedelta
import re
from typing import Collection
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, logger

from app.schemas.user import (
    AccountValidity,
    AccountValidityResponse,
    ForgotPasswordResponse,
    LoginData,
    UserCreate,
)
from app.services.email_service import send_email
from app.settings import settings
from app.security.security import get_password_hash, verify_password
from app.services.user_service import (
    create_user,
    get_user_by_username,
    get_user_by_email,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def decode_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired token",
        )


def verify_token(token: str, credentials_exception, db):
    payload = decode_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = get_user_by_username(username, db)
    if user is None:
        raise credentials_exception
    return user


def authenticate_user(username: str, password: str, db):
    user = get_user_by_username(username, db)
    if not user or not verify_password(pwd_context, password, user.hashed_password):
        return False
    return user


def verify_password_service(password: str, hashed_password: str):
    return verify_password(pwd_context, password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def generate_password_reset_token(email: str):
    return create_access_token(data={"sub": email}, expires_delta=timedelta(hours=1))


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


def validate_email(email):
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(regex, email):
        raise HTTPException(status_code=400, detail=f"Invalid email format: {email}")


def validate_moroccan_phone_number(phone_number):
    pattern = re.compile(r"^(?:\+212|0)(?:5[0-9]{8}|6[0-9]{8}|7[0-9]{8})$")
    if not pattern.match(phone_number):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Moroccan phone number format: {phone_number}",
        )


def validate_user_role(user_role: str):
    if not (user_role == "PRO" or user_role == "NORMAL"):
        raise HTTPException(status_code=400, detail="Role doesn't match")


def store_password_reset_token(email: str, token: str, db, expires_at: datetime):
    db["password_reset_tokens"].insert_one(
        {"email": email, "token": token, "expires_at": expires_at, "used": False}
    )


def mark_token_as_used(token: str, db):
    db["password_reset_tokens"].update_one({"token": token}, {"$set": {"used": True}})


def validate_reset_token(token: str, db):
    email = decode_token(token).get("sub")
    if not email or not get_user_by_email(email, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token or expired token",
        )
    return email


def generate_login_access_token(form_data: LoginData, db: Collection):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": True, "message": "Incorrect username or password"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    user_data = {
        "username": user.username,
        "role": user.role,
        "email": user.email,
        "consultation_balance": user.consultation_balance,
        # disabling user validity check for now
        "is_valid": True,
        "phoneNumber": user.phoneNumber,
    }

    return {
        "error": False,
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data,
    }


def handle_user_registration(user, db):
    if user.password != user.passwordConfirmation:
        raise HTTPException(status_code=400, detail="Confirm password does not match")

    validate_password_strength(user.password)
    validate_user_role(user.role)
    validate_email(user.email)
    validate_moroccan_phone_number(user.phoneNumber)

    user_data = AccountValidityResponse(
        username=user.username,
        is_valid=False,
        phoneNumber=user.phoneNumber,
        role=user.role,
        email=user.email,
        password=user.password,
    )
    try:
        return create_user(user=user_data, db=db)
    except HTTPException as e:
        raise e


async def handle_forgot_password(email, db):
    user = get_user_by_email(email.email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not registered"
        )
    token = create_access_token(
        data={"sub": user["email"]}, expires_delta=timedelta(minutes=15)
    )
    db["users"].update_one({"email": email.email}, {"$set": {"reset_token": token}})
    reset_link = f"http://localhost:4200/reset?token={token}"
    body = f"Hi, click on the link to reset your password: {reset_link}"
    try:
        await send_email(email.email, "Reset Your Password", body)
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email",
        )
    return ForgotPasswordResponse(
        message="Success",
        detail="Email sent successfully with reset instructions.",
        status=status.HTTP_200_OK,
    )


def handle_password_reset(reset_password_data, token, db):
    if reset_password_data.newPassword != reset_password_data.confirmNewPassword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match"
        )
    email = validate_reset_token(token, db)
    user = get_user_by_email(email, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    validate_password_strength(reset_password_data.newPassword)
    hashed_password = get_password_hash(pwd_context, reset_password_data.newPassword)
    db["users"].update_one(
        {"email": email},
        {"$set": {"hashed_password": hashed_password, "reset_token": None}},
    )
    return {"message": "Password reset successfully."}


def reset_password_for_logged_user(reset_password_data, db, token, current_user):
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    username = decode_token(token).get("sub")
    if username != current_user.username:
        raise HTTPException(status_code=403, detail="Token does not match")
    user = get_user_by_username(username, db)
    if not user or not verify_password_service(
        reset_password_data.oldPassword, user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    if reset_password_data.newPassword != reset_password_data.confirmNewPassword:
        raise HTTPException(status_code=400, detail="Confirm password does not match")
    validate_password_strength(reset_password_data.newPassword)
    hashed_password = get_password_hash(pwd_context, reset_password_data.newPassword)
    db["users"].update_one(
        {"username": user.username}, {"$set": {"hashed_password": hashed_password}}
    )
    return {"message": "Password reset successfully."}
