import pytest
from app.services.property import PropertyService
from app.services.property_import import property_import_service
from app.schemas.property import PropertyUpdate, SchoolCreate
from app.models import Property, PropertyEvent, School, Suburb


def create_test_suburb(db_session) -> Suburb:
    """Helper function to create a test suburb"""
    suburb = Suburb(
        name="Test Suburb",
        postcode="2000",
        state="NSW",
        region="Metropolitan",
        area="Inner City",
        properties_for_rent=100,
        properties_for_sale=200,
        population=50000,
        avg_age_range="25-34",
        owner_percentage=60.0,
        renter_percentage=40.0,
        family_percentage=45.0,
        single_percentage=55.0,
        median_price=1500000.0,
        median_rent=750.0,
        avg_days_on_market=30.0,
        auction_clearance_rate=75.0,
        entry_price=1000000.0,
        luxury_price=3000000.0,
        sales_growth={},
    )
    db_session.add(suburb)
    db_session.flush()
    return suburb


def create_test_property_data(suburb_id: int, property_id: str, listing_id: int) -> dict:
    """Helper function to create test property data"""
    return {
        "propertyId": property_id,
        "type": "House",
        "category": "Residential",
        "specifications": {
            "bedrooms": 3,
            "bathrooms": 2,
            "parkingSpaces": 1,
            "internal_area": 150.5,
            "land_area": 300.0,
        },
        "address": {
            "displayAddress": f"{property_id} Test Street",
            "postcode": "2000",
            "suburbName": "Test Suburb",
            "state": "NSW",
            "streetNumber": property_id.split("-")[1],
            "streetName": "Test",
            "streetType": "Street",
            "geolocation": {"latitude": -33.8688, "longitude": 151.2093},
        },
        "location": {
            "suburb": {
                "name": "Test Suburb",
                "state": "NSW",
                "region": "Metropolitan",
                "area": "Inner City",
                "postcode": "2000",
            }
        },
        "listing": {
            "id": listing_id,
            "url": f"https://example.com/property{listing_id}",
            "status": "Active",
            "type": "Sale",
            "displayPrice": "$1,000,000",
        },
        "marketStats": {
            "houses": {"forRent": 50, "forSale": 100},
            "apartmentsAndUnits": {"forRent": 30, "forSale": 60},
            "townhouses": {"forRent": 20, "forSale": 40},
        },
        "suburbInsights": {
            "medianPrice": 1500000.0,
            "medianRentPrice": 750.0,
            "avgDaysOnMarket": 30,
            "demographics": {
                "population": 50000,
                "avgAge": "25-34",
                "owners": 60.0,
                "renters": 40.0,
                "families": 45.0,
                "singles": 55.0,
            },
        },
        "schools": [],
        "images": [],
        "suburb_id": suburb_id,
    }


def cleanup_database(db_session):
    """Helper function to clean up the database"""
    db_session.query(PropertyEvent).delete()
    db_session.query(School).delete()
    db_session.query(Property).delete()
    db_session.query(Suburb).delete()
    db_session.commit()


def test_property_service_create(db_session):
    """Test property creation through service"""
    cleanup_database(db_session)

    service = PropertyService()
    suburb = create_test_suburb(db_session)

    property_data = create_test_property_data(suburb_id=suburb.id, property_id="TEST-2001", listing_id=2001)

    property = property_import_service.create_property_with_relations(db_session, property_data)
    assert property is not None, "Property creation failed"
    assert property.property_id == "TEST-2001"
    assert property.type == "House"
    assert property.suburb_id == suburb.id


def test_property_service_update(db_session):
    """Test property update through service"""
    cleanup_database(db_session)

    service = PropertyService()
    suburb = create_test_suburb(db_session)

    # First create a property
    property_data = create_test_property_data(suburb_id=suburb.id, property_id="TEST-2002", listing_id=2002)
    property = property_import_service.create_property_with_relations(db_session, property_data)
    assert property is not None, "Property creation failed"

    # Test update
    update_data = PropertyUpdate(
        property_id="TEST-2002",
        display_price="$1,100,000",
        listing_status="Under Offer",
        suburb_id=suburb.id,
        listing_url="https://example.com/property2",
        listing_type="Sale",
        market_stats={},
        images=[],
        suburb_insights={},
    )
    updated_property = service.update(db_session, db_obj=property, obj_in=update_data)
    assert updated_property.display_price == "$1,100,000"
    assert updated_property.listing_status == "Under Offer"


def test_property_service_display_price_update(db_session):
    """Test property display price update through service"""
    cleanup_database(db_session)

    service = PropertyService()
    suburb = create_test_suburb(db_session)

    # Create initial property
    property_data = create_test_property_data(suburb_id=suburb.id, property_id="TEST-2003", listing_id=2003)
    property = property_import_service.create_property_with_relations(db_session, property_data)
    assert property is not None, "Property creation failed"

    # Test price update
    updated_property = service.update_display_price(
        db_session, property_id=property.id, new_price="$1,100,000", category="Price Update", agency="Test Agency"
    )

    assert updated_property is not None
    assert updated_property.display_price == "$1,100,000"

    # Check timeline event was created
    timeline = service.get_timeline(db_session, property_id=property.id)
    assert len(timeline) == 1
    assert timeline[0].category == "Price Update"
    assert timeline[0].agency == "Test Agency"


def test_property_service_search(db_session):
    """Test property search functionality"""
    cleanup_database(db_session)

    service = PropertyService()
    suburb = create_test_suburb(db_session)

    # Create test properties
    property_data_list = [
        create_test_property_data(suburb.id, "TEST-2004", 2004),
        {
            **create_test_property_data(suburb.id, "TEST-2005", 2005),
            "type": "Apartment",
            "specifications": {
                "bedrooms": 2,
                "bathrooms": 1,
                "parkingSpaces": 1,
                "internal_area": 80.0,
                "land_area": None,
            },
            "listing": {
                "id": 2005,
                "url": "https://example.com/property5",
                "status": "Active",
                "type": "Sale",
                "displayPrice": "$800,000",
            },
        },
    ]

    for prop_data in property_data_list:
        property = property_import_service.create_property_with_relations(db_session, prop_data)
        assert property is not None, f"Property creation failed for {prop_data['propertyId']}"

    # Test search by suburb
    results = service.search_properties(db_session, suburb="Test Suburb")
    assert results is not None, "Search results should not be None"
    assert len(results) == 2, "Should find 2 properties in Test Suburb"

    # Test search by property type
    results = service.search_properties(db_session, property_type="House")
    assert results is not None, "Search results should not be None"
    assert len(results) == 1, "Should find 1 house"
    assert results[0] is not None, "First result should not be None"
    assert results[0].type == "House", "Property type should be House"

    # Test search by bedrooms
    results = service.search_properties(db_session, bedrooms=3)
    assert results is not None, "Search results should not be None"
    assert len(results) == 1, "Should find 1 property with 3 bedrooms"
    assert results[0] is not None, "First result should not be None"
    assert results[0].bedrooms == 3, "Property should have 3 bedrooms"


def test_property_import_service(db_session):
    """Test property import service"""
    cleanup_database(db_session)

    suburb = create_test_suburb(db_session)

    # Test property data
    test_data = create_test_property_data(suburb_id=suburb.id, property_id="TEST-2006", listing_id=2006)

    # Test data transformation
    transformed_data = property_import_service.transform_property_data(test_data, suburb.id)
    assert transformed_data["property_id"] == "TEST-2006"
    assert transformed_data["bedrooms"] == 3
    assert transformed_data["display_address"] == "TEST-2006 Test Street"

    # Test property creation with relationships
    property = property_import_service.create_property_with_relations(db_session, test_data)
    assert property is not None, "Property creation failed"
    assert property.property_id == "TEST-2006", "Property ID mismatch"
    assert property.suburb_id == suburb.id, "Suburb ID mismatch"
