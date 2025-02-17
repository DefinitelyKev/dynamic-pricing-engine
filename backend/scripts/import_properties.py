import os
import sys
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Add the parent directory to the Python path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Suburb, Property, School
from app.services.property_import import property_import_service


async def import_properties(db: Session, data: Dict) -> None:
    """Import properties into db from given dict"""

    try:
        initial_counts = {
            "properties": db.query(Property).count(),
            "schools": db.query(School).count(),
            "suburbs": db.query(Suburb).count(),
        }

        errors = []

        # Process each property
        for property_data in data.get("properties", []):
            try:
                # Create or get suburb
                suburb = property_import_service.create_or_get_suburb(db, property_data)
                if not suburb:
                    raise ValueError("Failed to create/get suburb")

                # Import property with suburb_id
                property_data["suburb_id"] = suburb.id
                imported_property = property_import_service.create_property_with_relations(db, property_data)
                if not imported_property:
                    raise ValueError("Failed to create/get property")

            except Exception as e:
                errors.append({"property_id": property_data.get("propertyId"), "error": str(e)})
                print(f"Error importing property {property_data.get('propertyId')}: {str(e)}")
                continue

        # Final commit
        db.commit()

        final_counts = {
            "properties": db.query(Property).count(),
            "schools": db.query(School).count(),
            "suburbs": db.query(Suburb).count(),
        }

        # Print results
        print(f"\nSuburbs created: {final_counts['suburbs'] - initial_counts['suburbs']}")
        print(f"Properties imported: {final_counts['properties'] - initial_counts['properties']}")
        print(f"Schools added: {final_counts['schools'] - initial_counts['schools']}")
        print(f"Errors encountered: {len(errors)}")

        if errors:
            print("\nErrors:")
            for error in errors:
                print(f"Property {error['property_id']}: {error['error']}")

    except SQLAlchemyError as e:
        print(f"Database error: {str(e)}")
        db.rollback()
        raise
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
