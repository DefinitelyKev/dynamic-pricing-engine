from sqlalchemy import String, Float, Boolean, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .base import BaseModel


class PricingRule(BaseModel):
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    conditions: Mapped[dict] = mapped_column(JSON)  # Stores rule conditions
    adjustments: Mapped[dict] = mapped_column(JSON)  # Stores price adjustment logic
    priority: Mapped[int] = mapped_column(Integer)
