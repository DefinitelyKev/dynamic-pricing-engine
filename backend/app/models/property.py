from __future__ import annotations
from typing import TYPE_CHECKING, List
from sqlalchemy import String, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel

if TYPE_CHECKING:
    from .pricing import PriceAdjustment
    from .suburb import Suburb


class Property(BaseModel):
    """Property model matching the domain.com.au data structure"""

    # Override id to use listing id. This will be the listing ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=False)
    property_id: Mapped[str] = mapped_column(String, index=True)  # e.g., "YG-2324-HR"
    type: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String)

    # Specifications
    bedrooms: Mapped[int] = mapped_column(Integer, nullable=True)
    bathrooms: Mapped[int] = mapped_column(Integer, nullable=True)
    parking_spaces: Mapped[int] = mapped_column(Integer, nullable=True)
    internal_area: Mapped[float] = mapped_column(Float, nullable=True)
    land_area: Mapped[float] = mapped_column(Float, nullable=True)

    # Address
    display_address: Mapped[str] = mapped_column(String)
    postcode: Mapped[str] = mapped_column(String)
    suburb_name: Mapped[str] = mapped_column(String)
    state: Mapped[str] = mapped_column(String)
    unit_number: Mapped[str] = mapped_column(String, nullable=True)
    street_number: Mapped[str] = mapped_column(String)
    street_name: Mapped[str] = mapped_column(String)
    street_type: Mapped[str] = mapped_column(String)

    # Geolocation
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)

    # Suburb relationship
    suburb_id: Mapped[int] = mapped_column(Integer, ForeignKey("suburb.id"))
    suburb: Mapped[Suburb] = relationship("Suburb", back_populates="properties")

    # Location details (denormalized for quick access)
    region: Mapped[str] = mapped_column(String, nullable=True)
    area: Mapped[str] = mapped_column(String, nullable=True)

    # Market stats
    market_stats: Mapped[dict] = mapped_column(JSON)

    # Listing details
    listing_url: Mapped[str] = mapped_column(String)
    listing_status: Mapped[str] = mapped_column(String)
    listing_type: Mapped[str] = mapped_column(String)
    display_price: Mapped[str] = mapped_column(String)

    # Additional data
    images: Mapped[dict] = mapped_column(JSON)  # Store image URLs
    suburb_insights: Mapped[dict] = mapped_column(JSON)

    # Relationships
    timeline: Mapped[List[PropertyEvent]] = relationship(
        "PropertyEvent", back_populates="property", cascade="all, delete-orphan"
    )
    schools: Mapped[List[School]] = relationship("School", back_populates="property", cascade="all, delete-orphan")
    price_adjustments: Mapped[List[PriceAdjustment]] = relationship(
        "PriceAdjustment", back_populates="property", cascade="all, delete-orphan"
    )


class PropertyEvent(BaseModel):
    """Model for property timeline events (sales, rentals)"""

    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("property.id"))
    event_price: Mapped[float] = mapped_column(Float)
    event_date: Mapped[str] = mapped_column(String)
    agency: Mapped[str] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String)
    days_on_market: Mapped[int] = mapped_column(Integer)
    price_description: Mapped[str] = mapped_column(String)

    property: Mapped[Property] = relationship("Property", back_populates="timeline")


class School(BaseModel):
    """Model for nearby schools"""

    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("property.id"))
    suburb_id: Mapped[int] = mapped_column(Integer, ForeignKey("suburb.id"))
    name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    sector: Mapped[str] = mapped_column(String)
    gender: Mapped[str] = mapped_column(String, nullable=True, default="Unknown")
    distance: Mapped[float] = mapped_column(Float)
    year_range: Mapped[str] = mapped_column(String, nullable=True, default="Not Specified")

    property: Mapped[Property] = relationship("Property", back_populates="schools")
    suburb_rel: Mapped[Suburb] = relationship("Suburb", back_populates="schools")
