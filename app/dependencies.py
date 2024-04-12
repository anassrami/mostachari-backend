# In dependencies.py
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