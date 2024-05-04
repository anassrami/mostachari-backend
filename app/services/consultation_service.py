# app/services/consultation_service.py

from bson import ObjectId
import requests
import pymongo
from fastapi import HTTPException, status
from pymongo.collection import Collection
from datetime import datetime
from bson.errors import InvalidId

from app.schemas.Consultation import Consultation, ConsultationCreate, ConsultationID

def is_valid_object_id(id):
    try:
        ObjectId(id)
        return True
    except InvalidId:
        return False
    
async def create_consultation(user_id: str, consultation_data: ConsultationCreate, db: Collection):
    # Prepare the payload for the POST request
    payload = {
        "openai_model": "gpt-4-0125-preview",  # Adjust the model name as needed
        "question": consultation_data.question,
        "categories": consultation_data.category
    }

    # URL of the external API
    url = "http://167.99.42.224/api/v1/mostachari_text_101/response"

    # Make the POST request using requests
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch AI response")

    response_data = response.json()
    print("Response Data:", response_data)  # Debug print

    # Check if there is an error in the response
    if response_data.get("error"):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response_data.get("error_message"))

    # Extract the AI response data
    data = response_data.get("data", {})
    aiResponse =  data.get("llm_responce", "No response received")
    articles_numbers = data.get("articles_numbers", "No response received")
    # Create the consultation document
    consultation = {
        "user_id": ObjectId(user_id),
        "category": consultation_data.category,
        "question": consultation_data.question,
        "title": consultation_data.title,
        "aiResponse": aiResponse,
        "articles_numbers" : articles_numbers,
        "creationDate": datetime.utcnow(),
        "is_active": 1
    }

    # Insert the consultation into the database
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
            .find({"user_id": ObjectId(user_id),"is_active":1},{"question": 0})
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


def get_consultation_by_id(id, user_id: str, db: Collection):
    if not is_valid_object_id(id):
     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid consultation ID format.")
    try:
        consultation = db['consultations'].find_one({"_id": ObjectId(id), "is_active": 1})
        if consultation and consultation.get("user_id") == ObjectId(user_id):
            consultation={**consultation, 'id': str(consultation['_id']), '_id': str(consultation['_id'])}
            if consultation:
                return ConsultationID(**consultation)  # Serialize result into Pydantic model
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active consultation found.")
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active consultation found.")
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active consultation found.")    

def delete_consultation(id, user_id: str, db: Collection):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid consultation ID format.")

    try:
        consultation = db['consultations'].find_one({"_id": ObjectId(id)})
        if consultation and consultation.get("user_id") == ObjectId(user_id):
            result = db['consultations'].find_one_and_update(
                {"_id": ObjectId(id), "is_active": 1},
                {"$set": {"is_active": 0}},
                return_document=pymongo.ReturnDocument.AFTER
            )
            if result:
                # Make sure to rename _id to id when passing to Pydantic
                result['id'] = str(result.pop('_id'))
                return ConsultationID(**result)  # Serialize result into Pydantic model
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active consultation found.")
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access attempt.")
    except pymongo.errors.PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))