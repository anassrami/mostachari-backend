# In dependencies.py
from fastapi import HTTPException, Request
from pymongo import MongoClient
from contextlib import contextmanager
from app.settings import settings
from pymongo.server_api import ServerApi


def get_database():
    client = MongoClient(settings.database_url, server_api=ServerApi('1'), tlsAllowInvalidCertificates=True)
    db = client[settings.database_name]
    try:
        yield db
    finally:
        client.close()
        
async def user_data_authorization(request: Request, username: str):
    if username and request.state.user != username:
        raise HTTPException(status_code=403, detail="Not authorized to access this user's data")
    return True
