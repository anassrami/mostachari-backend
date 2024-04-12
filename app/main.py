import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.server_api import ServerApi
from app.settings import settings
from app.api.v1 import auth, user
from app.dependencies import get_database
from app.services.auth_service import verify_token

app = FastAPI()
db_client = None
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Collection = Depends(get_database)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception, db)

# Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Including routers
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(user.router, prefix="/api/v1/user", dependencies=[Depends(get_current_user)])


@app.on_event("startup")
async def startup_event():
    global db_client
    db_client = MongoClient(settings.database_url, server_api=ServerApi('1'), tlsAllowInvalidCertificates=True)
    db = db_client[settings.database_name]
    # Just a simple operation to validate connection
    db.list_collection_names()

@app.on_event("shutdown")
async def shutdown_event():
    global db_client
    if db_client:
        db_client.close()