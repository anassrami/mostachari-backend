# User schema

from pydantic import BaseModel, EmailStr, Field

class LoginData(BaseModel):
    username: str
    password: str
    
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    is_active: bool
    consultation_balance: int
    class Config:
        from_attributes = True

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    password_confirmation: str = Field(alias="passwordConfirmation")

    # Use a Pydantic validator to ensure that the password and confirmation match
    @classmethod
    def validate_password(cls, values):
        if values.get('password') != values.get('password_confirmation'):
            raise ValueError("Passwords do not match")
        return values
