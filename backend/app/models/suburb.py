from __future__ import annotations
from typing import TYPE_CHECKING, List
from sqlalchemy import String, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .property import Property, School


class Suburb(BaseModel):
    """Suburb model containing demographic and market data"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    postcode: Mapped[str] = mapped_column(String, index=True)
    state: Mapped[str] = mapped_column(String)
    region: Mapped[str] = mapped_column(String, nullable=True)
    area: Mapped[str] = mapped_column(String, nullable=True)

    # Market statistics
    properties_for_rent: Mapped[int] = mapped_column(Integer, default=0)
    properties_for_sale: Mapped[int] = mapped_column(Integer, default=0)
    median_price: Mapped[float] = mapped_column(Float, nullable=True)
    median_rent: Mapped[float] = mapped_column(Float, nullable=True)
    avg_days_on_market: Mapped[float] = mapped_column(Float, nullable=True)

    # Demographics
    population: Mapped[int] = mapped_column(Integer, nullable=True)
    avg_age_range: Mapped[str] = mapped_column(String, nullable=True)
    owner_percentage: Mapped[float] = mapped_column(Float, nullable=True)
    renter_percentage: Mapped[float] = mapped_column(Float, nullable=True)
    family_percentage: Mapped[float] = mapped_column(Float, nullable=True)
    single_percentage: Mapped[float] = mapped_column(Float, nullable=True)

    # Additional insights
    entry_price: Mapped[float] = mapped_column(Float, nullable=True)
    luxury_price: Mapped[float] = mapped_column(Float, nullable=True)
    sales_growth: Mapped[dict] = mapped_column(JSON, default={})

    # Relationships
    properties: Mapped[List[Property]] = relationship("Property", back_populates="suburb", lazy="selectin")
    schools: Mapped[List[School]] = relationship("School", back_populates="suburb_rel", lazy="selectin")

    # Many-to-many relationship for surrounding suburbs
    surrounding_suburbs: Mapped[List[Suburb]] = relationship(
        "Suburb",
        secondary="suburb_surroundings",
        primaryjoin="Suburb.id == suburb_surroundings.c.suburb_id",
        secondaryjoin="Suburb.id == suburb_surroundings.c.surrounding_suburb_id",
        lazy="selectin",
    )


# Association table for suburb surroundings
from sqlalchemy import Table, Column, ForeignKey
from .base import Base

suburb_surroundings = Table(
    "suburb_surroundings",
    Base.metadata,
    Column("suburb_id", Integer, ForeignKey("suburb.id"), primary_key=True),
    Column("surrounding_suburb_id", Integer, ForeignKey("suburb.id"), primary_key=True),
)
