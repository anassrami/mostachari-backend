import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from app.settings import settings
from app.api.v1 import auth, consultation, user
from app.dependencies import get_database
from app.services.auth_service import verify_token
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError

app = FastAPI()
db_client = None

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip middleware for paths that begin with '/api/v1/auth'
        if not request.url.path.startswith("/api/v1/auth"):
            token = request.headers.get("Authorization")
            if token:
                try:
                    token = token.split(" ")[1]  # Assuming Bearer token
                    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
                    request.state.user = payload.get("sub")
                except JWTError:
                    return Response(status_code=401, content="Invalid token")
                except Exception as e:
                    return Response(status_code=401, content=str(e))

        response = await call_next(request)
        return response

# Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Apply the middleware
app.add_middleware(AuthMiddleware)

# Including routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/v1/user", tags=["user"])
app.include_router(consultation.router, prefix="/api/v1/consultations", tags=["consultations"])

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
