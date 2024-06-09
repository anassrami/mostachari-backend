from pydantic import BaseModel, EmailStr, Field

class PasswordReset(BaseModel):
    newPassword: str
    confirmNewPassword: str

class PasswordResetLoged(PasswordReset):
    oldPassword: str


class ForgotPassword(BaseModel):
    email :str

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
    hashed_password: str

    class Config:
        from_attributes = True

class UserDetails(UserBase):
    consultation_balance: int

    class Config:
        from_attributes = True

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    passwordConfirmation: str = Field(alias="passwordConfirmation")

    @classmethod
    def validate_password(cls, values):
        if values.get('password') != values.get('password_confirmation'):
            raise ValueError("Passwords do not match")
        return values
