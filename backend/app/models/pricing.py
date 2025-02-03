from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String, Float, Boolean, JSON, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import BaseModel

if TYPE_CHECKING:
    from .property import Property


class PricingRule(BaseModel):
    """Pricing rule model to work with domain.com.au property structure"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Rule conditions for domain-specific fields
    conditions: Mapped[dict] = mapped_column(
        JSON, default={}, comment="E.g., {'property_type': 'House', 'suburb': 'Calga'}"
    )

    # Price adjustments (percentage or fixed amount)
    adjustments: Mapped[dict] = mapped_column(JSON, default={}, comment="E.g., {'type': 'percentage', 'value': 10}")

    # Rule type (market-based or time-based)
    rule_type: Mapped[str] = mapped_column(String)

    # Priority for rule application
    priority: Mapped[int] = mapped_column(Integer)

    # Track rule effectiveness
    stats: Mapped[dict] = mapped_column(JSON, default={}, comment="Rule application statistics")

    # Relationships
    price_adjustments: Mapped[list[PriceAdjustment]] = relationship(
        "PriceAdjustment", back_populates="rule", cascade="all, delete-orphan"
    )


class PriceAdjustment(BaseModel):
    """Record of price adjustments made by pricing rules"""

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("property.id"))
    rule_id: Mapped[int] = mapped_column(Integer, ForeignKey("pricingrule.id"))

    # Original and adjusted prices (as strings to match domain.com.au format)
    original_price: Mapped[str] = mapped_column(String)
    adjusted_price: Mapped[str] = mapped_column(String)

    # Adjustment details
    adjustment_type: Mapped[str] = mapped_column(String)  # "percentage" or "fixed"
    adjustment_value: Mapped[float] = mapped_column(Float)

    # Market conditions at time of adjustment
    market_conditions: Mapped[dict] = mapped_column(
        JSON, default={}, comment="Market conditions when adjustment was made"
    )

    # Relations
    property: Mapped[Property] = relationship("Property", back_populates="price_adjustments")
    rule: Mapped[PricingRule] = relationship("PricingRule", back_populates="price_adjustments")
