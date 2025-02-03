from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from .base import BaseSchema, BaseModelSchema


class SuburbBase(BaseSchema):
    """Base schema for suburb data"""

    name: str
    postcode: str
    state: str
    region: Optional[str] = None
    area: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Market statistics
    properties_for_rent: int = 0
    properties_for_sale: int = 0
    median_price: Optional[float] = None
    median_rent: Optional[float] = None
    avg_days_on_market: Optional[float] = None
    auction_clearance_rate: Optional[float] = None

    # Demographics
    population: Optional[int] = None
    avg_age_range: Optional[str] = None
    owner_percentage: Optional[float] = None
    renter_percentage: Optional[float] = None
    family_percentage: Optional[float] = None
    single_percentage: Optional[float] = None

    # Additional insights
    entry_price: Optional[float] = None
    luxury_price: Optional[float] = None
    sales_growth: Dict = Field(default_factory=dict)


class SuburbCreate(SuburbBase):
    """Schema for creating a suburb"""

    pass


class SuburbUpdate(BaseSchema):
    """Schema for updating a suburb"""

    name: Optional[str] = None
    postcode: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    area: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    properties_for_rent: Optional[int] = None
    properties_for_sale: Optional[int] = None
    median_price: Optional[float] = None
    median_rent: Optional[float] = None
    avg_days_on_market: Optional[float] = None
    auction_clearance_rate: Optional[float] = None
    population: Optional[int] = None
    avg_age_range: Optional[str] = None
    owner_percentage: Optional[float] = None
    renter_percentage: Optional[float] = None
    family_percentage: Optional[float] = None
    single_percentage: Optional[float] = None
    entry_price: Optional[float] = None
    luxury_price: Optional[float] = None
    sales_growth: Optional[Dict] = None


class SuburbInDB(SuburbBase, BaseModelSchema):
    """Schema for suburb in database"""

    id: int
    surrounding_suburbs: List[int] = []  # List of surrounding suburb IDs


class Suburb(SuburbInDB):
    """Schema for complete suburb with relationships"""

    properties: List[int] = []  # List of property IDs
    schools: List[int] = []  # List of school IDs
