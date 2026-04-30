from enum import Enum
from fastapi import APIRouter, UploadFile, File, Form, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.listing import Listing
from app.db.deps import get_db
from app.agents.copywriter import generate_listing as run_crew
import json

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


# @router.post("/generate", response_model=ListingResponse)
@router.post("/generate")
async def generate_listing(
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    pictures: Optional[list[UploadFile]] = File(None),
    publication_type: Optional[PublicationType] = Form(None),
    shipping: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    # return ListingResponse(
    #     title=title,
    #     description=description,
    #     price=price,
    #     pictures=[p.filename for p in pictures],
    #     publication_type=publication_type,
    #     shipping=shipping,
    # )
    result = await run_crew(description)
    parsed = json.loads(str(result))



    draft = Listing(
        user_id="d9916e4b-43cc-4b71-909e-8c001590fd3a",
        generated_title=parsed["title"],
        generated_description=parsed["description"],
        price=price
    )

    db.add(draft)
    await db.commit()
    await db.refresh(draft)

    return {"draft_id": draft.id, "title": draft.generated_title, "description": draft.generated_description}



