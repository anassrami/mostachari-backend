from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME="moadgmc@outlook.com",
    MAIL_PASSWORD="Nino@123456",
    MAIL_FROM="mostachari@outlook.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp-mail.outlook.com",
    MAIL_STARTTLS=True,  # Correctly added as per the new model
    MAIL_SSL_TLS=False   # Correctly added as per the new model
)

try:
    fm = FastMail(conf)
    # your email sending logic here
except Exception as e:
    print(f"Failed to send email: {e}")

async def send_email(email: str, subject: str, body: str):
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=body,
            subtype="html"
        )
        await fm.send_message(message)
    except Exception as e:
        print(f"Failed to send email: {e}")

    
