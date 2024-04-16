# app/schemas/consultation.py

from bson import ObjectId
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class ConsultationBase(BaseModel):
    category: str
    question: str

class ConsultationCreate(ConsultationBase):
    pass

class Consultation(ConsultationBase):
    id: str
    creationDate: datetime = Field(default_factory=datetime.utcnow)

    @validator('id', pre=True, allow_reuse=True)
    def convert_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class ConsultationID(ConsultationBase):
    id: str = Field(..., alias='_id')
    aiResponse: Optional[str] = None
    creationDate: datetime = Field(default_factory=datetime.utcnow)

    @validator('id', pre=True, allow_reuse=True)
    def convert_id(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    class Config:
        orm_mode = True
        allow_population_by_field_name = True