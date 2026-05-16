from enum import Enum
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.listing import Listing
from app.db.deps import get_db
from app.agents.copywriter import generate_listing as run_crew
import json
import re

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


@router.post("/generate")
async def generate_listing(
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    pictures: Optional[list[UploadFile]] = File(None),
    publication_type: Optional[PublicationType] = Form(None),
    shipping: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    condition: Optional[str] = Form(None),
    listing_type_id: Optional[str] = Form(None),
    available_quantity: Optional[int] = Form(None)
):

    result = await run_crew(description)
    result_str = str(result)

    json_match = re.search(r'\{.*\}', result_str, re.DOTALL)
    if not json_match:
        raise HTTPException(status_code=500, detail="Agent failed to generate a valid listing")

    parsed = json.loads(json_match.group())

    draft = Listing(
        user_id="d9916e4b-43cc-4b71-909e-8c001590fd3a",
        generated_title=parsed["title"],
        generated_description=parsed["description"],
        price=price,
        category_id=parsed.get("category_id"),
        condition=condition,
        listing_type_id=listing_type_id,
        available_quantity=available_quantity,
        pictures=[] 
    )

    db.add(draft)
    await db.commit()
    await db.refresh(draft)

    return {"draft_id": draft.id, "title": draft.generated_title, "description": draft.generated_description,  "category_id": parsed.get("category_id"),
    "category_name": parsed.get("category_name")}



