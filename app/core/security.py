from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException
from dotenv import load_dotenv

import os

load_dotenv()

SECRET_KEY_JWT = os.getenv("SECRET_KEY_JWT")
ALGORITHM = "HS256"

def create_access_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(days=7)}
    token = jwt.encode(payload, SECRET_KEY_JWT, algorithm=ALGORITHM)
    return token

   


def verify_access_token(token: str) -> str:
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY_JWT, algorithms=[ALGORITHM])
        print(f"Decoded Claims: {decoded_payload}")
        return decoded_payload["sub"]
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid")



