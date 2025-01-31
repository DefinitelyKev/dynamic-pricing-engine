import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.property import PropertyCreate, PropertyUpdate, Property, PriceHistoryCreate
from app.schemas.pricing import PricingRuleCreate, PricingRuleUpdate


def test_property_create_schema():
    # Test valid property creation
    valid_property = PropertyCreate(
        name="Test Property",
        address="123 Test St",
        square_footage=1000.0,
        bedrooms=2,
        bathrooms=2.0,
        amenities={"parking": True},
        current_price=1500.0,
    )
    assert valid_property.name == "Test Property"
    assert valid_property.current_price == 1500.0

    # Test invalid property creation
    with pytest.raises(ValidationError):
        PropertyCreate(
            name="Test Property",
            address="123 Test St",
            square_footage=-1000.0,  # Invalid negative value
            bedrooms=2,
            bathrooms=2.0,
            amenities={"parking": True},
            current_price=1500.0,
        )


def test_property_update_schema():
    # Test partial update
    update_data = PropertyUpdate(current_price=2000.0)
    assert update_data.current_price == 2000.0
    assert update_data.name is None  # Other fields should be None


def test_price_history_create_schema():
    # Test valid price history creation
    valid_history = PriceHistoryCreate(property_id=1, price=1500.0, reason="Market adjustment")
    assert valid_history.price == 1500.0

    # Test invalid price
    with pytest.raises(ValidationError):
        PriceHistoryCreate(property_id=1, price=-1500.0, reason="Market adjustment")  # Invalid negative price


def test_pricing_rule_create_schema():
    # Test valid rule creation
    valid_rule = PricingRuleCreate(
        name="Summer Rule",
        description="Summer pricing adjustment",
        is_active=True,
        conditions={"season": "summer"},
        adjustments={"percentage": 10.0},
        priority=1,
    )
    assert valid_rule.name == "Summer Rule"
    assert valid_rule.priority == 1

    # Test invalid priority
    with pytest.raises(ValidationError):
        PricingRuleCreate(
            name="Invalid Rule",
            description="Test",
            is_active=True,
            conditions={},
            adjustments={},
            priority=-1,  # Invalid negative priority
        )
