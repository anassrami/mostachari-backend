

def verify_password(pwd_context, plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(pwd_context, password):
    return pwd_context.hash(password)