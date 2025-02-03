from __future__ import annotations
from typing import Optional, List, Dict, TYPE_CHECKING
from pydantic import BaseModel, Field
from datetime import datetime
from .base import BaseSchema, BaseModelSchema

if TYPE_CHECKING:
    from .pricing import PriceAdjustment
    from .suburb import SuburbInDB


class PropertySpecifications(BaseSchema):
    """Schema for property specifications"""

    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: Optional[int] = None
    internal_area: Optional[float] = None
    land_area: Optional[float] = None


class PropertyAddress(BaseSchema):
    """Schema for property address"""

    display_address: str
    postcode: str
    unit_number: Optional[str] = None
    street_number: str
    street_name: str
    street_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PropertyEventBase(BaseSchema):
    """Base schema for property timeline events"""

    event_price: float
    event_date: str
    agency: Optional[str] = None
    category: str
    days_on_market: int
    price_description: str


class PropertyEventCreate(PropertyEventBase):
    """Schema for creating property events"""

    property_id: int


class PropertyEvent(PropertyEventBase, BaseModelSchema):
    """Schema for complete property event"""

    property_id: int


class SchoolBase(BaseSchema):
    """Base schema for school information"""

    name: str
    type: str
    sector: str
    gender: str
    distance: float
    year_range: str


class SchoolCreate(SchoolBase):
    """Schema for creating schools"""

    property_id: int
    suburb_id: int


class School(SchoolBase, BaseModelSchema):
    """Schema for complete school information"""

    property_id: int
    suburb_id: int


class PropertyBase(BaseSchema):
    """Base schema for property information"""

    property_id: str = Field(description="External property identifier, e.g., YG-2324-HR")
    type: str = Field(description="Property type, e.g., House, Apartment")
    category: str = Field(description="Property category, e.g., Residential")
    specifications: PropertySpecifications
    address: PropertyAddress
    suburb_id: int = Field(description="ID of the associated suburb")

    # Market stats and listing details
    market_stats: Dict = Field(default_factory=dict)
    listing_url: str
    listing_status: str
    listing_type: str
    display_price: str

    # Optional fields
    region: Optional[str] = None
    area: Optional[str] = None

    # Additional data
    images: List[str] = Field(default_factory=list)
    suburb_insights: Dict = Field(default_factory=dict)


class PropertyCreate(PropertyBase):
    """Schema for creating properties"""

    id: int = Field(description="Listing ID to be used as primary key")


class PropertyUpdate(BaseSchema):
    """Schema for updating properties"""

    property_id: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    specifications: Optional[PropertySpecifications] = None
    address: Optional[PropertyAddress] = None
    suburb_id: Optional[int] = None
    market_stats: Optional[Dict] = None
    listing_status: Optional[str] = None
    listing_type: Optional[str] = None
    display_price: Optional[str] = None
    region: Optional[str] = None
    area: Optional[str] = None
    images: Optional[List[str]] = None
    suburb_insights: Optional[Dict] = None


class PropertyInDB(PropertyBase, BaseModelSchema):
    """Schema for property in database"""

    id: int = Field(description="Listing ID used as primary key")
    timeline: List[PropertyEvent] = []
    schools: List[School] = []


class Property(PropertyInDB):
    """Schema for complete property with all relationships"""

    from .suburb import SuburbInDB

    suburb: SuburbInDB  # Full suburb information
    price_adjustments: List["PriceAdjustment"] = []  # List of price adjustments

    class Config:
        from_attributes = True
