from .base import BaseSchema, BaseModelSchema
from .property import (
    Property,
    PropertyCreate,
    PropertyUpdate,
    PropertyEvent,
    PropertyEventCreate,
    School,
    SchoolCreate,
    PropertySpecifications,
    PropertyAddress,
)
from .pricing import PricingRule, PricingRuleCreate, PricingRuleUpdate, PriceAdjustment, PriceAdjustmentCreate
from .suburb import Suburb, SuburbCreate, SuburbUpdate, SuburbInDB
from .market_metrics import MarketMetrics, SuburbMetrics, PriceHistory, PropertyStats, SuburbPerformance, MarketSummary

__all__ = [
    "BaseSchema",
    "BaseModelSchema",
    "Property",
    "PropertyCreate",
    "PropertyUpdate",
    "PropertyEvent",
    "PropertyEventCreate",
    "School",
    "SchoolCreate",
    "PropertySpecifications",
    "PropertyAddress",
    "PricingRule",
    "PricingRuleCreate",
    "PricingRuleUpdate",
    "PriceAdjustment",
    "PriceAdjustmentCreate",
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
