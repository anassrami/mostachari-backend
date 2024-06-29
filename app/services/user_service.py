# User management logic
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
from jose import JWTError, jwt
from app.settings import settings

import pymongo
from pymongo.collection import Collection
from fastapi import HTTPException, status, Depends
from app.dependencies import get_database
from app.schemas.user import User, UserCreate, UserDetails
from app.security.security import get_password_hash
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(user: UserCreate, db: Collection = Depends(get_database)):
    hashed_password = get_password_hash(pwd_context, user.password)
    new_user = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "role" : user.role,
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
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    user_data ={
        "username": user.username,
        "email": user.email,
        "role" : user.role,
        "consultation_balance": 5,
    }
    return {
        "error": False,
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }
     


def get_user_by_username(username: str, db: Collection = Depends(get_database)) -> Optional[UserDetails]:
    user_data = db['users'].find_one({"username": username})
    if user_data:
        user_id = str(user_data.pop('_id'))  # Convert ObjectId to string and remove from user_data
        return User(id=user_id, **user_data)  # Create User instance using the retrieved data
    return None

def get_user_by_id(user_id: str,db):
    try:
        # Convert the string ID to ObjectId
        object_id = ObjectId(user_id)
    except Exception as e:
        raise ValueError("Invalid ObjectId format") from e
    
    # Fetch the user data from the database
    user_data = db['users'].find_one({"_id": object_id})
    return user_data

def get_user_by_email(email: str, db: Collection):
    user = db['users'].find_one({"email": email})
    if user is None:
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def user_change_role(user,  db ,role):

    if not (role == "PRO" or role == "NORMAL"):
        raise HTTPException(status_code=400, detail="Role doesn't match")
    
    if user.role == role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You're already using the same role."
        )

    if not isinstance(db, pymongo.database.Database):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database object is not valid."
        )

    query = {
        "_id": ObjectId(user.id),
        "is_active": True
    }
    update = {
        "$set": {"role": role}
    }
    result = db["users"].find_one_and_update(query, update, return_document=pymongo.ReturnDocument.AFTER)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or is not active."
        )

    return result
        