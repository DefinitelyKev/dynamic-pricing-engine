import pytest
from sqlalchemy import text
from datetime import datetime
from app.models import Property, PropertyEvent, School, PricingRule, Suburb


def test_database_connection(db_session):
    """Test database connection"""
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


def test_table_creation(db_session):
    """Test that all tables were created"""
    result = db_session.execute(
        text(
            """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """
        )
    )
    tables = {row[0] for row in result}

    expected_tables = {
        "property",
        "propertyevent",
        "school",
        "pricingrule",
        "priceadjustment",
        "suburb",
        "suburb_surroundings",
    }

    missing_tables = expected_tables - tables
    assert not missing_tables, f"Missing tables: {missing_tables}"


def test_can_create_suburb(db_session):
    """Test suburb creation"""
    test_suburb = Suburb(
        name="Test Suburb",
        postcode="2000",
        state="NSW",
        properties_for_rent=100,
        properties_for_sale=200,
        sales_growth={},
    )

    db_session.add(test_suburb)
    db_session.commit()

    result = db_session.query(Suburb).filter_by(name="Test Suburb").first()
    assert result is not None
    assert result.postcode == "2000"
    assert result.state == "NSW"


def test_can_create_property(db_session):
    """Test property creation with relationships"""
    # First create a suburb
    suburb = Suburb(
        name="Property Test Suburb",
        postcode="2000",
        state="NSW",
        properties_for_rent=100,
        properties_for_sale=200,
        sales_growth={},
    )
    db_session.add(suburb)
    db_session.flush()

    # Create property with a unique ID
    test_property = Property(
        id=1001,  # Unique ID
        property_id="TEST-1001",
        type="House",
        category="Residential",
        suburb_id=suburb.id,
        bedrooms=3,
        bathrooms=2,
        display_address="123 Test Street",
        postcode="2000",
        suburb_name="Property Test Suburb",
        state="NSW",
        street_number="123",
        street_name="Test",
        street_type="Street",
        market_stats={},
        listing_url="https://example.com/property1",
        listing_status="Active",
        listing_type="Sale",
        display_price="$1,000,000",
        images=[],
        suburb_insights={},
    )

    db_session.add(test_property)
    db_session.commit()

    result = db_session.query(Property).filter_by(property_id="TEST-1001").first()
    assert result is not None
    assert result.type == "House"
    assert result.suburb.name == "Property Test Suburb"


def test_can_create_property_event(db_session):
    """Test property event creation"""
    # Create suburb and property first
    suburb = Suburb(
        name="Event Test Suburb",
        postcode="2000",
        state="NSW",
        properties_for_rent=100,
        properties_for_sale=200,
        sales_growth={},
    )
    db_session.add(suburb)
    db_session.flush()

    property = Property(
        id=1002,  # Different unique ID
        property_id="TEST-1002",
        type="House",
        category="Residential",
        suburb_id=suburb.id,
        display_address="124 Test Street",
        postcode="2000",
        suburb_name="Event Test Suburb",
        state="NSW",
        street_number="124",
        street_name="Test",
        street_type="Street",
        market_stats={},
        listing_url="https://example.com/property2",
        listing_status="Active",
        listing_type="Sale",
        display_price="$1,000,000",
        images=[],
        suburb_insights={},
    )
    db_session.add(property)
    db_session.flush()

    # Create property event
    event = PropertyEvent(
        property_id=property.id,
        event_price=1000000.0,
        event_date="2025-02-03",
        category="PRICE_CHANGE",
        days_on_market=30,
        price_description="Price Reduced",
    )

    db_session.add(event)
    db_session.commit()

    result = db_session.query(PropertyEvent).filter_by(property_id=property.id).first()
    assert result is not None
    assert result.event_price == 1000000.0
    assert result.category == "PRICE_CHANGE"


def test_can_create_school(db_session):
    """Test school creation with relationships"""
    # Create suburb and property first
    suburb = Suburb(
        name="School Test Suburb",
        postcode="2000",
        state="NSW",
        properties_for_rent=100,
        properties_for_sale=200,
        sales_growth={},
    )
    db_session.add(suburb)
    db_session.flush()

    property = Property(
        id=1003,  # Another unique ID
        property_id="TEST-1003",
        type="House",
        category="Residential",
        suburb_id=suburb.id,
        display_address="125 Test Street",
        postcode="2000",
        suburb_name="School Test Suburb",
        state="NSW",
        street_number="125",
        street_name="Test",
        street_type="Street",
        market_stats={},
        listing_url="https://example.com/property3",
        listing_status="Active",
        listing_type="Sale",
        display_price="$1,000,000",
        images=[],
        suburb_insights={},
    )
    db_session.add(property)
    db_session.flush()

    # Create school
    school = School(
        property_id=property.id,
        suburb_id=suburb.id,
        name="Test School",
        type="Primary",
        sector="Public",
        gender="Co-ed",
        distance=1.5,
        year_range="K-6",
    )

    db_session.add(school)
    db_session.commit()

    result = db_session.query(School).filter_by(name="Test School").first()
    assert result is not None
    assert result.distance == 1.5
    assert result.property.property_id == "TEST-1003"
    assert result.suburb_rel.name == "School Test Suburb"
