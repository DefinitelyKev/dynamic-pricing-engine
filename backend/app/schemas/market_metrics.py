from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class MarketMetrics(BaseModel):
    """Base metrics model with common configuration"""

    model_config = ConfigDict(from_attributes=True)


class SuburbMetrics(MarketMetrics):
    """Schema for suburb-level metrics"""

    median_price: float = Field(ge=0)
    inventory: int = Field(ge=0)
    avg_days_on_market: float = Field(ge=0)
    price_growth: float


class PriceHistory(MarketMetrics):
    """Schema for historical price data"""

    date: str
    price_change: float


class PropertyStats(MarketMetrics):
    """Schema for property statistics"""

    month: str
    avg_price: float = Field(ge=0)
    inventory: int = Field(ge=0)


class SuburbPerformance(MarketMetrics):
    """Schema for suburb performance metrics"""

    name: str
    median_price: float = Field(ge=0)
    avg_days_on_market: float = Field(ge=0)
    sales_ratio: float = Field(ge=0, le=100)


class MarketSummary(MarketMetrics):
    """Schema for overall market summary"""

    total_properties: int = Field(ge=0)
    average_price: float = Field(ge=0)
    active_listings: int = Field(ge=0)
    updated_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
