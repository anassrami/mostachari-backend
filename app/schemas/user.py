from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class ForgotPassword(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str
    detail: str
    
class PasswordReset(BaseModel):
    newPassword: str
    confirmNewPassword: str

class PasswordResetLoged(PasswordReset):
    oldPassword: str

class LoginData(BaseModel):
    username: str
    password: str

class UserBase(BaseModel):
    username: str
    role : str
    phoneNumber : str
    email: EmailStr

class AccountValidity(UserBase):
    is_valid : bool

class UserCreate(UserBase):
    password: str

class User(AccountValidity):
    id: str
    is_active: bool
    consultation_balance: int
    hashed_password: str

    class Config:
        from_attributes = True

class UserDetails(AccountValidity):
    consultation_balance: int

    class Config:
        from_attributes = True

class UserRegister(UserCreate):
    passwordConfirmation: str = Field(alias="passwordConfirmation")

    @classmethod
    def validate_password(cls, values):
        if values.get('password') != values.get('password_confirmation'):
            raise ValueError("Passwords do not match")
        return values
    
class AccountValidityResponse(UserCreate):
    is_valid : bool

class ChangeRole(BaseModel):
    role :str

class ChangeMail(BaseModel):
    email :str

class VerifyMail(BaseModel):
    code :str