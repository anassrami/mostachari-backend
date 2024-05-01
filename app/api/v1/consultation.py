# api/consultation.py

from typing import List
from fastapi import APIRouter, Depends ,Query
from pymongo.collection import Collection
from app.dependencies import get_database
from app.schemas.Consultation import Consultation, ConsultationCreate, ConsultationID, Consultations
from app.utils.auth_utils import get_current_user  # Updated import
from app.services.consultation_service import create_consultation, delete_consultation, get_consultation_by_id, get_user_consultations

router = APIRouter()

@router.post("/consultation/create", response_model=ConsultationID)
def add_consultation(consultation_data: ConsultationCreate, db: Collection = Depends(get_database), current_user = Depends(get_current_user)):
    return create_consultation(current_user.id, consultation_data, db)

@router.put("/consultation/{id}", response_model=ConsultationID)
def update_consultation(id :str, db: Collection = Depends(get_database), current_user = Depends(get_current_user)):
    return delete_consultation(id,current_user.id, db)

@router.get("/consultation/{id}", response_model=ConsultationID)
def consultation_by_id(id :str, db: Collection = Depends(get_database), current_user = Depends(get_current_user)):
    return get_consultation_by_id(id,current_user.id, db)

@router.get("/consultations", response_model=List[Consultations])
def list_consultations(
    db: Collection = Depends(get_database),
    current_user = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number starting from 1"),
    size: int = Query(10, ge=1, description="Number of items per page")
):
    return get_user_consultations(current_user.id, db, page, size)
