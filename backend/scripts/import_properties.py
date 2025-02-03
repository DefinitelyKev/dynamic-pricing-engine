import os
import sys
import json
import asyncio
from typing import Dict, Any, Set

# Add the parent directory to the Python path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import Suburb, Property, School
from app.services.property_import import property_import_service


def create_suburb_from_property_data(db: Session, property_data: Dict[str, Any], created_suburbs: Set[str]) -> Suburb:
    """Create a suburb if it doesn't exist and return it"""

    # Extract suburb data from property
    location = property_data.get("location", {})
    suburb_info = location.get("suburb", {})

    if not suburb_info:
        raise ValueError("No suburb information found in property data")

    suburb_name = suburb_info.get("name")
    suburb_postcode = suburb_info.get("postcode")

    if not suburb_name or not suburb_postcode:
        raise ValueError("Missing required suburb information (name or postcode)")

    # Create suburb key for tracking
    suburb_key = f"{suburb_name}-{suburb_postcode}"

    # Check if suburb exists in database
    suburb = db.query(Suburb).filter_by(name=suburb_name, postcode=suburb_postcode).first()

    if not suburb:
        # Get market stats safely
        market_stats = property_data.get("marketStats", {})
        houses_stats = market_stats.get("houses", {})
        units_stats = market_stats.get("apartmentsAndUnits", {})
        townhouse_stats = market_stats.get("townhouses", {})

        # Get suburb insights safely
        suburb_insights = property_data.get("suburbInsights", {})
        demographics = suburb_insights.get("demographics", {})

        # Create new suburb
        suburb = Suburb(
            name=suburb_name,
            postcode=suburb_postcode,
            state=suburb_info.get("state"),
            region=suburb_info.get("region"),
            area=suburb_info.get("area"),
            # Market statistics
            properties_for_rent=(
                houses_stats.get("forRent", 0) + units_stats.get("forRent", 0) + townhouse_stats.get("forRent", 0)
            ),
            properties_for_sale=(
                houses_stats.get("forSale", 0) + units_stats.get("forSale", 0) + townhouse_stats.get("forSale", 0)
            ),
            # Demographics
            population=demographics.get("population"),
            avg_age_range=demographics.get("avgAge"),
            owner_percentage=demographics.get("owners"),
            renter_percentage=demographics.get("renters"),
            family_percentage=demographics.get("families"),
            single_percentage=demographics.get("singles"),
            # Additional insights
            median_price=suburb_insights.get("medianPrice"),
            median_rent=suburb_insights.get("medianRentPrice"),
            avg_days_on_market=suburb_insights.get("avgDaysOnMarket"),
            entry_price=suburb_insights.get("entryLevelPrice"),
            luxury_price=suburb_insights.get("luxuryLevelPrice"),
            # Sales growth data
            sales_growth=suburb_insights.get("salesGrowthList", {}),
        )

        db.add(suburb)
        db.flush()

        if suburb_key not in created_suburbs:
            created_suburbs.add(suburb_key)

    return suburb


async def import_properties(file_path: str):
    """Import properties from JSON file"""

    db = SessionLocal()
    created_suburbs = set()  # Track unique suburbs created

    try:
        print("Starting property import...")

        # Read the JSON file
        with open(file_path, "r") as f:
            data = json.load(f)
            properties_data = data.get("properties", [])

        print(f"Found {len(properties_data)} properties to import")

        # Track statistics
        stats = {"suburbs_created": 0, "properties_imported": 0, "schools_added": 0, "errors": []}

        # Process each property
        for idx, property_data in enumerate(properties_data, 1):
            try:
                # Create or get suburb
                suburb = create_suburb_from_property_data(db, property_data, created_suburbs)
                if not suburb:
                    raise ValueError("Failed to create/get suburb")

                # Import property with suburb_id
                property_data["suburb_id"] = suburb.id
                imported_property = property_import_service.create_property_with_relations(db, property_data)

                if imported_property:  # Only count if property was actually imported
                    stats["properties_imported"] += 1
                    stats["schools_added"] += len(property_data.get("schools", []))

                # Commit every 100 properties
                if idx % 100 == 0:
                    db.commit()
                    print(f"Imported {idx} properties...")

            except Exception as e:
                stats["errors"].append({"property_id": property_data.get("propertyId"), "error": str(e)})
                print(f"Error importing property {property_data.get('propertyId')}: {str(e)}")
                continue

        # Update suburbs created count
        stats["suburbs_created"] = len(created_suburbs)

        # Final commit
        db.commit()

        # Print results
        print("\nImport completed!")
        print(f"Suburbs created: {stats['suburbs_created']}")
        print(f"Properties imported: {stats['properties_imported']}")
        print(f"Schools added: {stats['schools_added']}")
        print(f"Errors encountered: {len(stats['errors'])}")

        if stats["errors"]:
            print("\nErrors:")
            for error in stats["errors"]:
                print(f"Property {error['property_id']}: {error['error']}")

    except Exception as e:
        print(f"Fatal error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python import_properties.py <path_to_json_file>")
        sys.exit(1)

    asyncio.run(import_properties(sys.argv[1]))
