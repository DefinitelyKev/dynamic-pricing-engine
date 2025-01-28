from sqlalchemy import Column, String, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import BaseModel


class Property(BaseModel):
    name: Mapped[str] = mapped_column(String, index=True)
    address: Mapped[str] = mapped_column(String)
    square_footage: Mapped[float] = mapped_column(Float)
    bedrooms: Mapped[int] = mapped_column(Integer)
    bathrooms: Mapped[float] = mapped_column(Float)
    amenities: Mapped[dict] = mapped_column(JSON)
    current_price: Mapped[float] = mapped_column(Float)

    price_history: Mapped[list["PriceHistory"]] = relationship("PriceHistory", back_populates="property")


class PriceHistory(BaseModel):
    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("property.id"))
    price: Mapped[float] = mapped_column(Float)
    reason: Mapped[str] = mapped_column(String)

    property: Mapped["Property"] = relationship("Property", back_populates="price_history")


class MarketData(BaseModel):
    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("property.id"))
    competitor_prices: Mapped[dict] = mapped_column(JSON)
    vacancy_rates: Mapped[float] = mapped_column(Float)
    seasonal_factors: Mapped[dict] = mapped_column(JSON)
    local_events: Mapped[dict] = mapped_column(JSON)
