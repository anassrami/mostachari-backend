# User routes for v1
from fastapi import APIRouter, Depends, HTTPException
from pymongo.collection import Collection

from app.dependencies import get_database
from app.schemas.user import ChangeMail, ChangeRole, UserDetails
from app.services.user_service import send_validation_code, user_change_mail, user_change_role
from app.utils.auth_utils import get_current_user

router = APIRouter()

@router.get("/details", response_model=UserDetails )
def read_user(user = Depends(get_current_user)):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/role", response_model=UserDetails )
def read_user(roleObject: ChangeRole ,user = Depends(get_current_user), db: Collection = Depends(get_database)):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_change_role(user,  db , roleObject.role)

@router.put("/email", response_model=UserDetails )
def read_user(mailObject: ChangeMail ,user = Depends(get_current_user), db: Collection = Depends(get_database)):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_change_mail(user,  db , mailObject.email)

@router.post("/sendValidationCode")
async def read_user(user = Depends(get_current_user), db: Collection = Depends(get_database)):
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return await send_validation_code(user, db)