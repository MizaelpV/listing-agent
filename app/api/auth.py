from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from app.db.deps import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.redis import set_token
from app.models.user import User, UserToken
from urllib import parse
import httpx 
import os

load_dotenv()



router = APIRouter()

MELI_CLIENT_ID = os.getenv("MELI_CLIENT_ID")
MELI_REDIRECT_URI = os.getenv("MELI_REDIRECT_URI")
MELI_CLIENT_SECRET = os.getenv("MELI_CLIENT_SECRET")

if not MELI_CLIENT_ID or not MELI_REDIRECT_URI or not MELI_CLIENT_SECRET:
    raise ValueError("Missing required environment variables: MELI_CLIENT_ID, MELI_REDIRECT_URI, MELI_CLIENT_SECRET")



@router.get("/")
async def get_auth():
    return {"status": "ok"}

@router.get("/login")
async def login():
    params = {
        "response_type": "code",
        "client_id": MELI_CLIENT_ID,
        "redirect_uri": MELI_REDIRECT_URI,
        "scope": "offline_access read write" 
    }
    query_string = parse.urlencode(params)
    url = f"https://auth.mercadolibre.cl/authorization?{query_string}"

    return RedirectResponse(url)

@router.get("/callback")
async def get_callback(code: str, db: AsyncSession = Depends(get_db)):
    meli_payload = {
        "grant_type": "authorization_code",
        "client_id": MELI_CLIENT_ID, 
        "client_secret": MELI_CLIENT_SECRET,
        "code": code,
        "redirect_uri": MELI_REDIRECT_URI
    }

    url = "https://api.mercadolibre.com/oauth/token"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=meli_payload)
        response.raise_for_status()
        token_data = response.json()

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    meli_user_id = token_data["user_id"]
    result = await db.execute(select(User).where(User.meli_id == str(meli_user_id)))
    user = result.scalar_one_or_none()

    if not user: 
        user = User(meli_id=str(meli_user_id))
        db.add(user)
        await db.commit()
        await db.refresh(user)

    
    token_result = await db.execute(select(UserToken).where(UserToken.provider == "mercadolibre").where(UserToken.user_id == user.id))

    existing_token = token_result.scalar_one_or_none()

    if existing_token:
        existing_token.access_token = access_token
        existing_token.refresh_token = refresh_token   
    else:
        user_token = UserToken(
            user_id=user.id,
            provider="mercadolibre",
            access_token=access_token,
            refresh_token=refresh_token
        )
        db.add(user_token)

    await db.commit()

    await set_token(f"meli_access_token:{user.id}", access_token, ttl=6*60*60)

    return {"status": "ok", "user_id": str(user.id)}
 
   

    