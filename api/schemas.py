from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class ListingResponse(BaseModel):
    id: int
    url: Optional[str] = None
    broker_name: Optional[str] = None
    description: Optional[str] = None
    price_raw: Optional[str] = None
    price_numeric: Optional[float] = None
    currency: Optional[str] = None
    features: Optional[List[str]] = None
    property_size_m2: Optional[float] = None
    transaction_type: Optional[str] = None
    date_posted: Optional[date] = None
    location: Optional[str] = None
    image: Optional[str] = None
    posting_type: Optional[str] = None
    publisher_logo: Optional[str] = None
    country: Optional[str] = None

    model_config = {"from_attributes": True}


class PaginatedListings(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[ListingResponse]
