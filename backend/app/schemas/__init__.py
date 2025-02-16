from .base import BaseSchema, BaseModelSchema
from .property import (
    Property,
    PropertyCreate,
    PropertyUpdate,
    School,
    SchoolCreate,
    PropertySpecifications,
    PropertyAddress,
)
from .suburb import Suburb, SuburbCreate, SuburbUpdate, SuburbInDB
from .market_metrics import MarketMetrics, SuburbMetrics, PriceHistory, PropertyStats, SuburbPerformance, MarketSummary

__all__ = [
    "BaseSchema",
    "BaseModelSchema",
    "Property",
    "PropertyCreate",
    "PropertyUpdate",
    "School",
    "SchoolCreate",
    "PropertySpecifications",
    "PropertyAddress",
    "Suburb",
    "SuburbCreate",
    "SuburbUpdate",
    "SuburbInDB",
    "MarketMetrics",
    "SuburbMetrics",
    "PriceHistory",
    "PropertyStats",
    "SuburbPerformance",
    "MarketSummary",
]
