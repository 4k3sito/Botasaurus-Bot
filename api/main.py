from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from database import get_db
from models import Listing
from schemas import ListingResponse, PaginatedListings

app = FastAPI(title="Real Estate Listings API", version="1.0.0")


@app.get("/listings", response_model=PaginatedListings, summary="List listings with optional filters")
def get_listings(
    transaction_type: Optional[str] = Query(None, description="rent or sale"),
    location: Optional[str] = Query(None, description="Partial match, e.g. 'Cancún'"),
    min_price: Optional[float] = Query(None, description="Minimum price (parsed numeric)"),
    max_price: Optional[float] = Query(None, description="Maximum price (parsed numeric)"),
    min_size: Optional[float] = Query(None, description="Min property size in m²"),
    max_size: Optional[float] = Query(None, description="Max property size in m²"),
    date_from: Optional[date] = Query(None, description="Posted on or after (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Posted on or before (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Listing)

    if transaction_type:
        q = q.filter(Listing.transaction_type.ilike(f"%{transaction_type}%"))
    if location:
        q = q.filter(Listing.location.ilike(f"%{location}%"))
    if min_price is not None:
        q = q.filter(Listing.price_numeric >= min_price)
    if max_price is not None:
        q = q.filter(Listing.price_numeric <= max_price)
    if min_size is not None:
        q = q.filter(Listing.property_size_m2 >= min_size)
    if max_size is not None:
        q = q.filter(Listing.property_size_m2 <= max_size)
    if date_from:
        q = q.filter(Listing.date_posted >= date_from)
    if date_to:
        q = q.filter(Listing.date_posted <= date_to)

    total = q.count()
    data = q.order_by(Listing.id).offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedListings(total=total, page=page, page_size=page_size, data=data)


@app.get("/listings/{listing_id}", response_model=ListingResponse, summary="Get a single listing by ID")
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing
