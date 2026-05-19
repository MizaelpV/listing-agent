from enum import Enum
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.listing import Listing, ListingStatus
from app.db.deps import get_db
from app.agents.copywriter import generate_listing as run_crew
from app.db.redis import get_token
from app.db.deps import get_current_user
from app.core.meli_auth import get_valid_meli_token
import json
import re
import httpx

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
    current_user = Depends(get_current_user),
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
        user_id=current_user,
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


@router.post("/publish/{draft_id}")
async def publish_listing(draft_id: str, db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    draft_result = await db.execute(select(Listing).where(Listing.id == draft_id))
    draft = draft_result.scalar_one_or_none()

    if not draft:
        raise HTTPException(status_code=404, detail="No draft found")

    if draft.user_id != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to publish this draft")    

    token = await get_valid_meli_token(draft.user_id, db)


    url = "https://api.mercadolibre.com/items"

    meli_payload = {
        "title": draft.generated_title,
        "category_id": draft.category_id,
        "price": draft.price,
        "buying_mode": "buy_it_now",
        "currency_id": "CLP",
        "condition": draft.condition,
        "listing_type_id": draft.listing_type_id or "free",
        "available_quantity": draft.available_quantity,
         "pictures": draft.pictures or [
        {"source": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Culinary_fruits_front_view.jpg/1200px-Culinary_fruits_front_view.jpg"}
    ],
        "attributes": [
        {"id": "BRAND", "value_name": "Generic"},
        {"id": "GTIN", "value_name": "0123456789012"}
       ]
    }
    
    async with httpx.AsyncClient() as client:
        headers={"Authorization": f"Bearer {token}"}
        response =  await client.post(url, json=meli_payload, headers=headers)

        if response.status_code != 200:
            print("MeLi error:", response.json())  


        response.raise_for_status()
        
        meli_response = response.json()

        draft.meli_item_id = meli_response["id"]
        draft.meli_url = meli_response["permalink"]
        draft.status = ListingStatus.published
    
    await db.commit()
    await db.refresh(draft) 
    
    return {"meli_url": draft.meli_url, "meli_item_id": draft.meli_item_id}

