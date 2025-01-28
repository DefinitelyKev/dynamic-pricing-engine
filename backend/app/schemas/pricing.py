from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseModelSchema


class PricingRuleBase(BaseSchema):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    conditions: Dict[str, Any] = Field(default_factory=dict)
    adjustments: Dict[str, float] = Field(default_factory=dict)
    priority: int = Field(ge=0)


class PricingRuleCreate(PricingRuleBase):
    pass


class PricingRuleUpdate(PricingRuleBase):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    conditions: Optional[Dict[str, Any]] = None
    adjustments: Optional[Dict[str, float]] = None
    priority: Optional[int] = None


class PricingRule(PricingRuleBase, BaseModelSchema):
    pass
