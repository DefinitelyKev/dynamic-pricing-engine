import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.property import (
    PropertyCreate,
    PropertyUpdate,
    PropertyEvent,
    PropertyEventCreate,
    School,
    SchoolCreate,
)
from app.schemas.pricing import (
    PricingRuleCreate,
    PricingRuleUpdate,
    PriceAdjustmentCreate,
)
from app.schemas.suburb import SuburbCreate, SuburbUpdate


def test_property_create_schema():
    # Test valid property creation
    valid_property = PropertyCreate(
        id=12345,
        property_id="TEST-123",
        type="House",
        category="Residential",
        suburb_id=1,
        bedrooms=3,
        bathrooms=2,
        parking_spaces=1,
        internal_area=150.5,
        land_area=300.0,
        display_address="123 Test Street",
        postcode="2000",
        suburb_name="TestSuburb",
        state="NSW",
        street_number="123",
        street_name="Test",
        street_type="Street",
        market_stats={},
        listing_url="https://example.com/property",
        listing_status="Active",
        listing_type="Sale",
        display_price="$1,000,000",
        images=[],
        suburb_insights={},
    )
    assert valid_property.property_id == "TEST-123"
    assert valid_property.type == "House"


def test_property_update_schema():
    # Test partial update with all required fields
    update_data = PropertyUpdate(
        property_id="TEST-123",
        display_price="$1,100,000",
        listing_status="Under Offer",
        # Required fields must be included even in updates
        suburb_id=1,
        listing_url="https://example.com/property",
        listing_type="Sale",
        market_stats={},
        images=[],
        suburb_insights={},
    )
    assert update_data.display_price == "$1,100,000"
    assert update_data.listing_status == "Under Offer"


def test_property_event_create_schema():
    # Test valid event creation
    valid_event = PropertyEventCreate(
        property_id=1,
        event_price=1000000.0,
        event_date="2025-02-03",
        category="PRICE_CHANGE",
        days_on_market=30,
        price_description="Price Reduced",
    )
    assert valid_event.event_price == 1000000.0


def test_school_create_schema():
    # Test valid school creation
    valid_school = SchoolCreate(
        property_id=1,
        suburb_id=1,
        name="Test School",
        type="Primary",
        sector="Public",
        gender="Co-ed",
        distance=1.5,
        year_range="K-6",
    )
    assert valid_school.name == "Test School"


def test_pricing_rule_create_schema():
    # Test valid rule creation
    valid_rule = PricingRuleCreate(
        name="Test Rule",
        description="Test Description",
        is_active=True,
        conditions={"property_type": "House"},
        adjustments={"percentage": 5.0},
        rule_type="market_based",
        priority=1,
        stats={},
    )
    assert valid_rule.name == "Test Rule"


def test_suburb_create_schema():
    # Test valid suburb creation
    valid_suburb = SuburbCreate(
        name="Test Suburb",
        postcode="2000",
        state="NSW",
        properties_for_rent=100,
        properties_for_sale=200,
        sales_growth={},
    )
    assert valid_suburb.name == "Test Suburb"
