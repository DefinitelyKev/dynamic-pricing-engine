# scripts/import_properties.py

import json
import asyncio
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import Suburb, Property, School
from app.services.property_import import property_import_service


def create_suburb_from_property_data(db: Session, property_data: Dict[str, Any]) -> Suburb:
    """Create a suburb if it doesn't exist and return it"""

    # Extract suburb data from property
    suburb_data = {
        "name": property_data["location"]["suburb"]["name"],
        "postcode": property_data["location"]["suburb"]["postcode"],
        "state": property_data["location"]["suburb"]["state"],
        "region": property_data["location"]["suburb"]["region"],
        "area": property_data["location"]["suburb"]["area"],
    }

    # Check if suburb exists
    suburb = db.query(Suburb).filter_by(name=suburb_data["name"], postcode=suburb_data["postcode"]).first()

    if not suburb:
        # Create new suburb with market stats
        suburb = Suburb(
            **suburb_data,
            properties_for_rent=property_data["marketStats"]["houses"]["forRent"]
            + property_data["marketStats"]["apartmentsAndUnits"]["forRent"]
            + property_data["marketStats"]["townhouses"]["forRent"],
            properties_for_sale=property_data["marketStats"]["houses"]["forSale"]
            + property_data["marketStats"]["apartmentsAndUnits"]["forSale"]
            + property_data["marketStats"]["townhouses"]["forSale"],
            # Demographics from suburbInsights
            population=property_data["suburbInsights"]["demographics"]["population"],
            avg_age_range=property_data["suburbInsights"]["demographics"]["avgAge"],
            owner_percentage=property_data["suburbInsights"]["demographics"]["owners"],
            renter_percentage=property_data["suburbInsights"]["demographics"]["renters"],
            family_percentage=property_data["suburbInsights"]["demographics"]["families"],
            single_percentage=property_data["suburbInsights"]["demographics"]["singles"],
        )
        db.add(suburb)
        db.flush()  # Get the ID without committing

    return suburb


async def import_properties(file_path: str):
    """Import properties from JSON file"""

    db = SessionLocal()
    try:
        print("Starting property import...")

        # Read the JSON file
        with open(file_path, "r") as f:
            data = json.load(f)
            properties_data = data["properties"]

        print(f"Found {len(properties_data)} properties to import")

        # Track statistics
        stats = {"suburbs_created": 0, "properties_imported": 0, "schools_added": 0, "errors": []}

        # Process each property
        for idx, property_data in enumerate(properties_data, 1):
            try:
                # Create or get suburb
                suburb = create_suburb_from_property_data(db, property_data)
                if not hasattr(suburb, "id"):
                    stats["suburbs_created"] += 1

                # Import property with suburb_id
                property_data["suburb_id"] = suburb.id
                imported_property = property_import_service.create_property_with_relations(db, property_data)

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
    import sys

    if len(sys.argv) != 2:
        print("Usage: python import_properties.py <path_to_json_file>")
        sys.exit(1)

    asyncio.run(import_properties(sys.argv[1]))
