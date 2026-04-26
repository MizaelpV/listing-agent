from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
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
async def get_callback(code: str):
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
        return response.json()


 
   

    