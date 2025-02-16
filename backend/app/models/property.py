from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict
from sqlalchemy import String, Float, Integer, ForeignKey, Table, Column
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel, Base

if TYPE_CHECKING:
    from .suburb import Suburb

# Association table for property-school relationship
property_school = Table(
    "property_school",
    Base.metadata,
    Column("property_id", Integer, ForeignKey("property.id"), primary_key=True),
    Column("school_id", Integer, ForeignKey("school.id"), primary_key=True),
    Column("distance", Float, nullable=True),
)


class Property(BaseModel):
    """Property model matching the domain.com.au data structure"""

    # Override id to use listing id. This will be the listing ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=False)
    type: Mapped[str] = mapped_column(String, nullable=True)

    # Suburb relationship
    suburb_id: Mapped[int] = mapped_column(Integer, ForeignKey("suburb.id"))
    suburb: Mapped[Suburb] = relationship("Suburb", back_populates="properties")

    # Listing details
    display_price: Mapped[str] = mapped_column(String, nullable=True)
    listing_status: Mapped[str] = mapped_column(String, nullable=True)
    listing_mode: Mapped[str] = mapped_column(String, nullable=True)
    listing_method: Mapped[str] = mapped_column(String, nullable=True)
    listing_url: Mapped[str] = mapped_column(String, unique=True)

    # Specifications
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[int] = mapped_column(Integer)
    parking_spaces: Mapped[int] = mapped_column(Integer)
    land_area: Mapped[int] = mapped_column(Integer)
    features: Mapped[List[str]] = mapped_column(ARRAY(String))
    structured_features: Mapped[List[Dict[str, str]]] = mapped_column(JSONB)

    # Address
    address: Mapped[str] = mapped_column(String, nullable=True)
    unit_number: Mapped[str] = mapped_column(String, nullable=True)
    street_number: Mapped[str] = mapped_column(String, nullable=True)
    street_name: Mapped[str] = mapped_column(String, nullable=True)
    suburb_name: Mapped[str] = mapped_column(String, nullable=True)
    postcode: Mapped[str] = mapped_column(String, nullable=True)
    state: Mapped[str] = mapped_column(String, nullable=True)

    # Additional data
    images: Mapped[List[str]] = mapped_column(ARRAY(String))  # Store image URLs

    # Relationships
    schools: Mapped[List[School]] = relationship("School", secondary=property_school, back_populates="properties")


class School(BaseModel):
    """Model for nearby schools"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String, nullable=True)
    education_level: Mapped[str] = mapped_column(String, nullable=True)
    year_range: Mapped[str] = mapped_column(String, nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=True)
    gender: Mapped[str] = mapped_column(String, nullable=True)
    state: Mapped[str] = mapped_column(String, nullable=True)
    postcode: Mapped[str] = mapped_column(String, nullable=True)
    suburb_id: Mapped[int] = mapped_column(Integer, ForeignKey("suburb.id"))

    # Relationships
    properties: Mapped[List[Property]] = relationship("Property", secondary=property_school, back_populates="schools")
    suburb_rel: Mapped[Suburb] = relationship("Suburb", back_populates="schools")
