import pytest
from app.services.property import PropertyService
from app.schemas.property import PropertyCreate, PropertyUpdate, MarketDataCreate
from app.models.property import Property, PriceHistory, MarketData


def test_property_service_create(db_session):
    service = PropertyService()

    # Test property creation
    property_data = PropertyCreate(
        name="Service Test Property",
        address="789 Test St",
        square_footage=1200.0,
        bedrooms=3,
        bathrooms=2.0,
        amenities={"parking": True},
        current_price=2000.0,
    )

    property = service.create(db_session, obj_in=property_data)
    assert property.name == "Service Test Property"
    assert property.current_price == 2000.0


def test_property_service_update(db_session):
    service = PropertyService()

    # First create a property
    property_data = PropertyCreate(
        name="Update Test Property",
        address="101 Test St",
        square_footage=1000.0,
        bedrooms=2,
        bathrooms=1.0,
        amenities={},
        current_price=1500.0,
    )
    property = service.create(db_session, obj_in=property_data)

    # Test update
    update_data = PropertyUpdate(current_price=1600.0)
    updated_property = service.update(db_session, db_obj=property, obj_in=update_data)
    assert updated_property.current_price == 1600.0


def test_property_service_price_update(db_session):
    service = PropertyService()

    # Create initial property
    property_data = PropertyCreate(
        name="Price Update Test",
        address="202 Test St",
        square_footage=900.0,
        bedrooms=1,
        bathrooms=1.0,
        amenities={},
        current_price=1300.0,
    )
    property = service.create(db_session, obj_in=property_data)

    # Test price update
    updated_property = service.update_price(
        db_session, property_id=property.id, new_price=1400.0, reason="Market adjustment"
    )

    assert updated_property is not None, "Price update failed"
    assert updated_property.current_price == 1400.0

    # Check price history
    history = service.get_price_history(db_session, property_id=property.id)
    assert len(history) == 1
    assert history[0].price == 1400.0


def test_property_service_market_data(db_session):
    service = PropertyService()

    # Create property
    property_data = PropertyCreate(
        name="Market Data Test",
        address="303 Test St",
        square_footage=800.0,
        bedrooms=1,
        bathrooms=1.0,
        amenities={},
        current_price=1100.0,
    )
    property = service.create(db_session, obj_in=property_data)
    assert property is not None

    # Test market data update
    market_data = MarketDataCreate(
        property_id=property.id,
        competitor_prices={"Comp1": 1200.0, "Comp2": 1000.0},
        vacancy_rates=0.05,
        seasonal_factors={"summer": 1.1},
        local_events={"event1": "Festival"},
    )

    # Create/Update market data
    updated_market_data = service.update_market_data(db_session, property_id=property.id, market_data=market_data)

    # Add assertions with null checks
    assert updated_market_data is not None
    assert updated_market_data.vacancy_rates == 0.05
    assert updated_market_data.competitor_prices == {"Comp1": 1200.0, "Comp2": 1000.0}

    # Test updating existing market data
    new_market_data = MarketDataCreate(
        property_id=property.id,
        competitor_prices={"Comp1": 1300.0, "Comp2": 1100.0},
        vacancy_rates=0.06,
        seasonal_factors={"summer": 1.2},
        local_events={"event1": "Festival", "event2": "Conference"},
    )

    updated_market_data = service.update_market_data(db_session, property_id=property.id, market_data=new_market_data)

    assert updated_market_data is not None
    assert updated_market_data.vacancy_rates == 0.06
    assert updated_market_data.competitor_prices == {"Comp1": 1300.0, "Comp2": 1100.0}


def test_property_service_market_data_nonexistent_property(db_session):
    service = PropertyService()

    # Try to update market data for non-existent property
    market_data = MarketDataCreate(
        property_id=99999,  # Non-existent ID
        competitor_prices={"Comp1": 1200.0},
        vacancy_rates=0.05,
        seasonal_factors={"summer": 1.1},
        local_events={"event1": "Festival"},
    )

    result = service.update_market_data(db_session, property_id=99999, market_data=market_data)

    assert result is None
