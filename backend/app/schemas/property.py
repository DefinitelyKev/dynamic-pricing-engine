from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from .base import BaseSchema, BaseModelSchema


class PropertyBase(BaseSchema):
    name: str
    address: str
    square_footage: float = Field(gt=0)
    bedrooms: int = Field(ge=0)
    bathrooms: float = Field(ge=0)
    amenities: Dict[str, bool] = Field(default_factory=dict)
    current_price: float = Field(gt=0)


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(PropertyBase):
    name: Optional[str] = None
    address: Optional[str] = None
    square_footage: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    amenities: Optional[Dict[str, bool]] = None
    current_price: Optional[float] = None


class PriceHistoryBase(BaseSchema):
    price: float = Field(gt=0)
    reason: Optional[str] = None


class PriceHistoryCreate(PriceHistoryBase):
    property_id: int


class PriceHistory(PriceHistoryBase, BaseModelSchema):
    property_id: int


class Property(PropertyBase, BaseModelSchema):
    price_history: List[PriceHistory] = []


class MarketDataBase(BaseSchema):
    competitor_prices: Dict[str, float]
    vacancy_rates: float = Field(ge=0, le=1)
    seasonal_factors: Dict[str, float]
    local_events: Dict[str, str]


class MarketDataCreate(MarketDataBase):
    property_id: int


class MarketData(MarketDataBase, BaseModelSchema):
    property_id: int
