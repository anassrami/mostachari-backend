# Configuration and settings
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()  # This function loads environment variables from the .env file

class Settings(BaseSettings):
    database_url: str = os.getenv('DATABASE_URL')
    database_name: str = os.getenv('DATABASE_NAME')
    secret_key: str = os.getenv('API_SECRET_KEY')
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30


settings = Settings()
