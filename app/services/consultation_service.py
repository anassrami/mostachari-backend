# app/services/consultation_service.py

from bson import ObjectId
import pymongo
from fastapi import HTTPException, status
from pymongo.collection import Collection
from datetime import datetime

from app.schemas.Consultation import ConsultationCreate

def create_consultation(user_id: str, consultation_data: ConsultationCreate, db: Collection):
    consultation = {
        "user_id": ObjectId(user_id),
        "category": consultation_data.category,
        "question": consultation_data.question,
        "aiResponse": None,  # This would be generated possibly by an AI model or could be added later
        "creationDate": datetime.utcnow()
    }
    try:
        result = db['consultations'].insert_one(consultation)
        consultation['_id'] = str(result.inserted_id)
        return consultation
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



def get_user_consultations(user_id: str, db: Collection, page: int, size: int):
    skip_amount = (page - 1) * size
    try:
        consultations = list(
            db['consultations']
            .find({"user_id": ObjectId(user_id)})
            .skip(skip_amount)
            .limit(size)
        )
        return consultations
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

