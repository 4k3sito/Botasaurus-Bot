from sqlalchemy import Column, Integer, String, Text, Float, Date
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text)
    broker_name = Column(String(255), index=True)
    description = Column(Text)
    price_raw = Column(String(255))
    price_numeric = Column(Float, nullable=True, index=True)
    currency = Column(String(10), nullable=True)
    features = Column(ARRAY(String), nullable=True)
    property_size_m2 = Column(Float, nullable=True, index=True)
    transaction_type = Column(String(50), index=True)
    date_posted = Column(Date, nullable=True, index=True)
    location = Column(String(255), index=True)
    image = Column(Text, nullable=True)
    posting_type = Column(String(50), nullable=True)
    publisher_logo = Column(Text, nullable=True)
    country = Column(String(100), nullable=True)
