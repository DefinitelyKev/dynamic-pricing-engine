from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from .base import BaseSchema, BaseModelSchema


class PricingRuleBase(BaseSchema):
    """Base schema for pricing rules"""

    name: str
    description: Optional[str] = None
    is_active: bool = True
    conditions: Dict[str, Any] = Field(
        default_factory=dict, description="Rule conditions (e.g., property_type, suburb)"
    )
    adjustments: Dict[str, float] = Field(default_factory=dict, description="Price adjustment parameters")
    rule_type: str = Field(description="Type of rule (market_based or time_based)")
    priority: int = Field(ge=0, description="Rule application priority")
    stats: Dict[str, Any] = Field(default_factory=dict, description="Rule effectiveness statistics")


class PricingRuleCreate(PricingRuleBase):
    """Schema for creating pricing rules"""

    pass


class PricingRuleUpdate(BaseSchema):
    """Schema for updating pricing rules"""

    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    conditions: Optional[Dict[str, Any]] = None
    adjustments: Optional[Dict[str, float]] = None
    rule_type: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0)
    stats: Optional[Dict[str, Any]] = None


class PricingRule(PricingRuleBase, BaseModelSchema):
    """Schema for complete pricing rule"""

    id: int


class PriceAdjustmentBase(BaseSchema):
    """Base schema for price adjustments"""

    property_id: int
    rule_id: int
    original_price: str = Field(description="Original price as string (e.g., '$500,000')")
    adjusted_price: str = Field(description="Adjusted price as string (e.g., '$525,000')")
    adjustment_type: str = Field(description="Type of adjustment (percentage or fixed)")
    adjustment_value: float = Field(description="Adjustment value (e.g., 5.0 for 5%)")
    market_conditions: Dict[str, Any] = Field(
        default_factory=dict, description="Market conditions at time of adjustment"
    )


class PriceAdjustmentCreate(PriceAdjustmentBase):
    """Schema for creating price adjustments"""

    pass


class PriceAdjustment(PriceAdjustmentBase, BaseModelSchema):
    """Schema for complete price adjustment"""

    id: int
