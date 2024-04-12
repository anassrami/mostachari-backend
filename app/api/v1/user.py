# User routes for v1
from fastapi import APIRouter, Depends, HTTPException
from pymongo.collection import Collection

from app.dependencies import get_database
from app.schemas.user import User, UserCreate
from app.services.user_service import create_user, get_user_by_username

router = APIRouter()

@router.get("/users/{username}", response_model=User)
def read_user(username: str, db: Collection = Depends(get_database)):
    db_user = get_user_by_username(username, db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
