# Authentication routes for v1
from fastapi import APIRouter, Depends, Query, status
from pymongo.collection import Collection
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.dependencies import get_database
from app.schemas.user import ForgotPassword, ForgotPasswordResponse, LoginData, PasswordReset, PasswordResetLoged, UserRegister
from app.services.auth_service import (
    handle_forgot_password,
    generate_login_access_token,
    handle_user_registration,
    reset_password_for_logged_user,
    handle_password_reset
)
from app.utils.auth_utils import get_current_user

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/token")
def login_for_access_token(form_data: LoginData, db: Collection = Depends(get_database)):
    return generate_login_access_token(form_data, db)

@router.post("/register")
def register_user(user: UserRegister, db=Depends(get_database)):
    return handle_user_registration(user, db)

@router.post("/forgot-password", response_model=ForgotPasswordResponse, status_code=status.HTTP_200_OK)
async def forgot_password(email: ForgotPassword, db=Depends(get_database)):
    return handle_forgot_password(email, db)

@router.post("/reset-password")
async def reset_password(reset_password_data: PasswordReset, token: str = Query(...), db=Depends(get_database)):
    return handle_password_reset(reset_password_data, token, db)

@router.post("/logged/reset-password")
async def reset_password_for_logged_user(
    reset_password_data: PasswordResetLoged,
    db=Depends(get_database),
    token: str = Depends(oauth2_scheme),
    current_user=Depends(get_current_user)
):
    return reset_password_for_logged_user(reset_password_data, db, token, current_user)
