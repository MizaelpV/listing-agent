from app.db.database import SessionLocal
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_access_token

security = HTTPBearer()


async def get_db():
    async with SessionLocal() as session:
        yield session


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    user_id = verify_access_token(credentials.credentials)
    return user_id
