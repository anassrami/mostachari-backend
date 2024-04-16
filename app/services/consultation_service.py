# app/services/consultation_service.py

from bson import ObjectId
import pymongo
from fastapi import HTTPException, status
from pymongo.collection import Collection
from datetime import datetime

from app.schemas.Consultation import Consultation, ConsultationCreate

def create_consultation(user_id: str, consultation_data: ConsultationCreate, db: Collection):
    consultation = {
        "user_id": ObjectId(user_id),
        "category": consultation_data.category,
        "question": consultation_data.question,
        "aiResponse": None,  # This would be generated possibly by an AI model or could be added later
        "creationDate": datetime.utcnow(),
        "is_active":1
    }
    try:
        result = db['consultations'].insert_one(consultation)
        consultation['id'] = str(result.inserted_id)
        return consultation
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def get_user_consultations(user_id: str, db: Collection, page: int, size: int):
    skip_amount = (page - 1) * size
    try:
        consultations = list(
            db['consultations']
            .find({"user_id": ObjectId(user_id),"is_active":1})
            .skip(skip_amount)
            .limit(size)
        )
        converted_consultations = [
        {**consultation, 'id': str(consultation['_id']), '_id': str(consultation['_id'])}
        for consultation in consultations
        ]
        return converted_consultations
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



def delete_consultation(id, user_id: str, db: Collection):
    try:
        consultation = db['consultations'].find_one({"_id": ObjectId(id)})
        if consultation and consultation.get("user_id") == ObjectId(user_id):
            result = db['consultations'].find_one_and_update(
                {"_id": ObjectId(id), "is_active": 1},
                {"$set": {"is_active": 0}},
                return_document=pymongo.ReturnDocument.AFTER
            )
            if result:
                return Consultation(**result)  # Serialize result into Pydantic model
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active consultation found.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access attempt.")
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))