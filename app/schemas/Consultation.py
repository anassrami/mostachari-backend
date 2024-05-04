from bson import ObjectId
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import List, Optional

class ConsultationsBase(BaseModel):
    category: List[str]
    title: str

class ConsultationBase(BaseModel):
    category: List[str]
    question: str
    title: str

class Consultations(ConsultationsBase):
    id: str
    creationDate: datetime = Field(default_factory=datetime.utcnow)

    @validator('id', pre=True, allow_reuse=True)
    def convert_id(cls, v):
        return str(v) if isinstance(v, ObjectId) else v

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class ConsultationCreate(ConsultationBase):
    pass

class Consultation(ConsultationBase):
    id: str
    creationDate: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('id', pre=True, allow_reuse=True)
    def convert_id(cls, v):
        return str(v) if isinstance(v, ObjectId) else v

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class ConsultationID(ConsultationBase):
    id: str = Field(..., alias='id')
    aiResponse: Optional[str]
    articles_numbers: List[str] = Field(default_factory=list)
    creationDate: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('id', pre=True, allow_reuse=True)
    def convert_id(cls, v):
        return str(v) if isinstance(v, ObjectId) else v

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
