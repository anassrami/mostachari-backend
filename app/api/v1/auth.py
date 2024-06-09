# Authentication routes for v1
from datetime import timedelta
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.collection import Collection

from app.security.security import get_password_hash
from app.services.email_service import send_email
from app.settings import settings
from app.dependencies import get_database
from app.schemas.user import LoginData, PasswordReset, UserCreate, UserRegister
from app.services.auth_service import authenticate_user, create_access_token, generate_password_reset_token, validate_password_strength, verify_password_reset_token, verify_password_service
from app.services.user_service import create_user, get_user_by_email, get_user_by_username 
from passlib.context import CryptContext

from fastapi.security import OAuth2PasswordBearer
from app.utils.auth_utils import get_current_user  # Updated import


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/token")
def login_for_access_token(form_data: LoginData, db: Collection = Depends(get_database)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Prepare user data for response, excluding sensitive information like hashed_password
    user_data = {
        "username": user.username,
        "email": user.email,
        "consultation_balance": user.consultation_balance,  # Provide a default value if key doesn't exist
    }

    return {
        "error": False,
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

@router.post("/register")
def register_user(user: UserRegister, db=Depends(get_database)):

    if user.password != user.passwordConfirmation:
        raise HTTPException(status_code=400, detail="Confirm password does not match")
    
    validate_password_strength(user.password)

    user_data = UserCreate(
        username=user.username,
        email=user.email,
        password=user.password
    )
    try:
        new_user = create_user(user=user_data, db=db)
        return new_user
    except HTTPException as e:
        raise e

@router.post("/forgot-password")
async def forgot_password(request: Request, email: str = Body(...),db=Depends(get_database)):
    user = get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")
    token = generate_password_reset_token(email)
    reset_link = f"{request.url_for('reset_password')}?token={token}"
    body = f"Hi, click on the link to reset your password: {reset_link}"
    await send_email(email, "Reset Your Password", body)
    return {"message": "Email sent successfully with reset instructions."}

@router.post("/loged/reset-password")
async def reset_password(
    resetPassword: PasswordReset,
    db=Depends(get_database),
    token: str = Depends(oauth2_scheme),
    current_user=Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    username = verify_password_reset_token(token)

    if username != current_user.username:
        raise HTTPException(status_code=403, detail="Token does not match")

    user = get_user_by_username(username, db)
    print(user.hashed_password)

    if not user or not verify_password_service(resetPassword.oldPassword, user.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    if resetPassword.newPassword != resetPassword.confirmNewPassword:
        raise HTTPException(status_code=400, detail="Confirm password does not match")

    validate_password_strength(resetPassword.newPassword)

    hashed_password = get_password_hash(pwd_context, resetPassword.newPassword)
    db['users'].update_one({"username": user.username}, {"$set": {"hashed_password": hashed_password}})

    return {"message": "Password reset successfully."}
