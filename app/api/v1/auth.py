# Authentication routes for v1
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.collection import Collection

from app.settings import settings
from app.dependencies import get_database
from app.schemas.user import LoginData, UserCreate, UserRegister
from app.services.auth_service import authenticate_user, create_access_token
from app.services.user_service import create_user


router = APIRouter()

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
