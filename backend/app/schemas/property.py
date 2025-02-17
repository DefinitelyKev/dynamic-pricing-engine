from __future__ import annotations
from typing import Optional, List, Dict, TYPE_CHECKING
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from .base import BaseSchema, BaseModelSchema

if TYPE_CHECKING:
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
    suburb_name: str
    state: str
    unit_number: Optional[str] = None
    street_number: str
    street_name: str
    street_type: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


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
    suburb_id: int = Field(description="ID of the associated suburb")

    # These can be provided either as nested objects or flat fields
    specifications: Optional[PropertySpecifications] = None
    address: Optional[PropertyAddress] = None

    # Flattened specification fields (used if specifications object not provided)
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: Optional[int] = None
    internal_area: Optional[float] = None
    land_area: Optional[float] = None

    # Flattened address fields (used if address object not provided)
    display_address: Optional[str] = None
    postcode: Optional[str] = None
    suburb_name: Optional[str] = None
    state: Optional[str] = None
    unit_number: Optional[str] = None
    street_number: Optional[str] = None
    street_name: Optional[str] = None
    street_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Location details
    region: Optional[str] = None
    area: Optional[str] = None

    # Market stats and listing details
    market_stats: Dict = Field(default_factory=dict)
    listing_url: str
    listing_status: str
    listing_type: str
    display_price: str

    # Additional data
    images: List[str] = Field(default_factory=list)
    suburb_insights: Dict = Field(default_factory=dict)

    def model_post_init(self, _context) -> None:
        """Post initialization hook to handle both nested and flat data"""
        # If specifications object is provided, use its values
        if self.specifications:
            self.bedrooms = self.specifications.bedrooms
            self.bathrooms = self.specifications.bathrooms
            self.parking_spaces = self.specifications.parking_spaces
            self.internal_area = self.specifications.internal_area
            self.land_area = self.specifications.land_area

        # If address object is provided, use its values
        if self.address:
            self.display_address = self.address.display_address
            self.postcode = self.address.postcode
            self.suburb_name = self.address.suburb_name
            self.state = self.address.state
            self.unit_number = self.address.unit_number
            self.street_number = self.address.street_number
            self.street_name = self.address.street_name
            self.street_type = self.address.street_type
            self.latitude = self.address.latitude
            self.longitude = self.address.longitude


class PropertyCreate(PropertyBase):
    """Schema for creating properties"""

    id: int = Field(description="Listing ID to be used as primary key")


class PropertyUpdate(PropertyBase):
    """Schema for updating properties"""

    property_id: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    id: Optional[int] = None


class PropertyInDB(PropertyBase, BaseModelSchema):
    """Schema for property in database"""

    id: int = Field(description="Listing ID used as primary key")
    schools: List[School] = Field(default_factory=list)


class Property(PropertyInDB):
    """Schema for complete property with all relationships"""

    suburb: Optional["SuburbInDB"] = None

    model_config = ConfigDict(from_attributes=True)
