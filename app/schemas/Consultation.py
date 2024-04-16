# app/schemas/consultation.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ConsultationBase(BaseModel):
    category: str
    question: str

class ConsultationCreate(ConsultationBase):
    pass

class Consultation(ConsultationBase):
    aiResponse: Optional[str] = None
    creationDate: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True