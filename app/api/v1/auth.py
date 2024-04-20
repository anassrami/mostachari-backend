# Authentication routes for v1
from datetime import timedelta
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.collection import Collection

from app.security.security import get_password_hash
from app.services.email_service import send_email
from app.settings import settings
from app.dependencies import get_database
from app.schemas.user import LoginData, UserCreate, UserRegister
from app.services.auth_service import authenticate_user, create_access_token, generate_password_reset_token, verify_password_reset_token
from app.services.user_service import create_user, get_user_by_email
from passlib.context import CryptContext

from fastapi.security import OAuth2PasswordBearer
from app.utils.auth_utils import get_current_user  # Updated import


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

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
        "id": str(user.id),  # Convert ObjectId to string
        "username": user.username,
        "email": user.email,
        "consultation_balance": user.consultation_balance,  # Provide a default value if key doesn't exist
        "is_active": user.is_active  # Provide a default value if key doesn't exist
    }

    return {
        "error": False,
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }



@router.post("/register")
def register_user(user: UserRegister, db=Depends(get_database)):
    # The password confirmation check is done in the UserRegister model
    # Now we prepare the data for user creation
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

@router.post("/reset-password")
async def reset_password(token: str = Body(...), new_password: str = Body(...),db=Depends(get_database)):
    email = verify_password_reset_token(token)
    user = get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = get_password_hash(pwd_context, new_password)
    db['users'].update_one({"email": email}, {"$set": {"hashed_password": hashed_password}})
    return {"message": "Password reset successfully."}

@router.post("/loged/reset-password")
async def reset_password(new_password: str = Body(...),db=Depends(get_database),token: str = Depends(oauth2_scheme), current_user = Depends(get_current_user)):
    email = verify_password_reset_token(token)
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = get_password_hash(pwd_context, new_password)
    db['users'].update_one({"email": email}, {"$set": {"hashed_password": hashed_password}})
    return {"message": "Password reset successfully."}