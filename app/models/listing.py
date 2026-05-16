from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy import Enum as SAEnum    
from app.db.database import Base
import uuid
import datetime

class ListingStatus(str, Enum):
    draft = "draft"
    published = "published"
    failed = "failed"


class Listing(Base):
    __tablename__ = "listing_drafts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    generated_title = Column(String, nullable=False)
    generated_description = Column(String, nullable=False)
    price = Column(Integer, default=0)
    status = Column(SAEnum(ListingStatus), default=ListingStatus.draft)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    category_id = Column(String, nullable=True)
    condition = Column(String)
    listing_type_id = Column(String)
    available_quantity = Column(Integer)
    pictures = Column(JSON, nullable=True)
    meli_item_id = Column(String, nullable=True)
    meli_url = Column(String, nullable=True)