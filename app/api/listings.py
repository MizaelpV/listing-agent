from enum import Enum
from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class PublicationType(str, Enum):
    classic = "classic"
    premium = "gold_premium" 


class ListingResponse(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: float
    pictures: Optional[list[str]] = []
    publication_type: PublicationType
    shipping: str


@router.get("/")
async def get_listings():
    return {"status": "ok"}


@router.post("/generate", response_model=ListingResponse)
async def generate_listing(
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    pictures: list[UploadFile] = File(...),
    publication_type: Optional[PublicationType] = Form(None),
    shipping: Optional[str] = Form(None),
):
    return ListingResponse(
        title=title,
        description=description,
        price=price,
        pictures=[p.filename for p in pictures],
        publication_type=publication_type,
        shipping=shipping,
    )