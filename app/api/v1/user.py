# User routes for v1
from fastapi import APIRouter, Depends, HTTPException
from pymongo.collection import Collection

from app.dependencies import get_database
from app.schemas.user import User
from app.services.user_service import get_user_by_username
from app.utils.auth_utils import get_current_user

router = APIRouter()

@router.get("/details", response_model=User )
def read_user(username = Depends(get_current_user), db: Collection = Depends(get_database)):
    db_user = get_user_by_username(username.username, db)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
