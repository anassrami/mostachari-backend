from pydantic import BaseModel

class ConnectionConfig(BaseModel):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool  # Ensure this is defined if it's required
    MAIL_SSL_TLS: bool   # Ensure this is defined if it's required