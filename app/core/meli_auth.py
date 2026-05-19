from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.redis import get_token, set_token
from app.models.user import UserToken
from dotenv import load_dotenv
import httpx
import os

load_dotenv()

MELI_CLIENT_ID = os.getenv("MELI_CLIENT_ID")
MELI_CLIENT_SECRET = os.getenv("MELI_CLIENT_SECRET")


async def get_valid_meli_token(user_id: str, db: AsyncSession) -> str:
    token_in_redis = await get_token(f"meli_access_token:{user_id}")

    if (token_in_redis):
        return token_in_redis.decode("utf-8")
  
    token_result = await db.execute(select(UserToken).where(UserToken.provider == "mercadolibre").where(UserToken.user_id == user_id))
    existing_token = token_result.scalar_one_or_none()

    if not (existing_token):
        raise HTTPException(status_code=401, detail="There is not available token")
    
    meli_payload = {
        "grant_type": "refresh_token",
        "client_id": MELI_CLIENT_ID, 
        "client_secret": MELI_CLIENT_SECRET,
        "refresh_token": existing_token.refresh_token
    }

    url = "https://api.mercadolibre.com/oauth/token"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=meli_payload)
        response.raise_for_status()
        token_data = response.json()
        
        access_token = token_data["access_token"] 
        refresh_token = token_data["refresh_token"]

    await set_token(f"meli_access_token:{user_id}", access_token, ttl=6*60*60)

    existing_token.access_token = access_token
    existing_token.refresh_token = refresh_token

    await db.commit()

    return access_token
