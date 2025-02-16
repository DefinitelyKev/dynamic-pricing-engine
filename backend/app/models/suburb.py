from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Any
from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .property import Property, School


class Suburb(BaseModel):
    """Suburb model containing demographic and market data"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    postcode: Mapped[str] = mapped_column(String, index=True)
    state: Mapped[str] = mapped_column(String, nullable=True)
    suburb_profile_url: Mapped[str] = mapped_column(String, unique=True)

    # Demographics
    population: Mapped[int] = mapped_column(Integer, nullable=True)
    avg_age_range: Mapped[str] = mapped_column(String, nullable=True)
    owner_percentage: Mapped[float] = mapped_column(Float, nullable=True)
    renter_percentage: Mapped[float] = mapped_column(Float, nullable=True)
    family_percentage: Mapped[float] = mapped_column(Float, nullable=True)
    single_percentage: Mapped[float] = mapped_column(Float, nullable=True)

    # Additional insights
    median_price: Mapped[float] = mapped_column(Float, nullable=True)
    median_rent: Mapped[float] = mapped_column(Float, nullable=True)
    avg_days_on_market: Mapped[float] = mapped_column(Float, nullable=True)
    entry_price: Mapped[float] = mapped_column(Float, nullable=True)
    luxury_price: Mapped[float] = mapped_column(Float, nullable=True)
    sales_growth: Mapped[Mapped[List[Dict[str, Any]]]] = mapped_column(JSONB, default=list, nullable=True)

    # Relationships
    properties: Mapped[List[Property]] = relationship("Property", back_populates="suburb", lazy="selectin")
    schools: Mapped[List[School]] = relationship("School", back_populates="suburb_rel", lazy="selectin")
