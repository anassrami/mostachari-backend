# User management logic
from typing import Optional

import pymongo
from pymongo.collection import Collection
from fastapi import HTTPException, status, Depends
from app.dependencies import get_database
from app.schemas.user import User, UserCreate
from app.security.security import get_password_hash
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(user: UserCreate, db: Collection = Depends(get_database)):
    hashed_password = get_password_hash(pwd_context, user.password)
    new_user = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "is_active": True,
        "consultation_balance": 5,
    }
    try:
        db['users'].insert_one(new_user)
    except pymongo.errors.DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered."
        )
    new_user['_id'] = str(new_user['_id'])
    return new_user


def get_user_by_username(username: str, db: Collection = Depends(get_database)) -> Optional[User]:
    user_data = db['users'].find_one({"username": username}, {"_id": 1, "username": 1, "email": 1, "is_active": 1, "consultation_balance": 1, "hashed_password": 1})
    if user_data:
        user_id = str(user_data.pop('_id'))  # Convert ObjectId to string and remove from user_data
        return User(id=user_id, **user_data)  # Create User instance using the retrieved data
    return None


