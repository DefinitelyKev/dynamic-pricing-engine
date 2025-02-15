import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.property import Property, PropertyEvent, School
from app.schemas.property import PropertyCreate, PropertyEventCreate, SchoolCreate


class PropertyImportService:
    def transform_property_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw JSON data to match our schema structure"""

        # Get specifications safely
        listing_summary = data.get("listingSummary", {})

        transformed = {
            # Required fields with defaults
            "id": data.get("listingId"),
            "type": data.get("propertyType", "Unknown"),
            "suburb_id": data.get("suburb_id"),
            # Listing Details
            "display_price": data.get("displayPrice", "Price not provided"),
            "listing_status": listing_summary.get("status", "N/A"),
            "listing_mode": data.get("mode", "N/A"),
            "listing_method": data.get("method", "N/A"),
            "listing_url": data.get("listingUrl"),
            # Specifications
            "bedrooms": data.get("beds"),
            "bathrooms": data.get("baths"),
            "parking_spaces": data.get("parking"),
            "area_stats": listing_summary.get("stats"),
            "features": data.get("features"),
            "structured_features": data.get("structuredFeatures"),
            # Address
            "address": listing_summary.get("address", "N/A"),
            "unit_number": data.get("unitNumber"),
            "street_number": data.get("streetNumber", ""),
            "street_name": data.get("street", ""),
            "suburb_name": data.get("suburb", ""),
            "postcode": data.get("postcode", ""),
            "state": data.get("state", ""),
            # Additional data
            "images": data.get("images", []),
            "schools": data.get("schools"),
        }

        return {k: v for k, v in transformed.items() if v is not None}

    def create_schools_from_property_data(self, db: Session, property_data: Dict[str, Any]) -> None:
        for school_data in property_data["schools"]:
            school_id = property_data.get("id")
            if not school_id:
                continue

            existing_school = db.query(School).filter(School.id == school_id).first()
            if existing_school:
                continue

            school = School(
                school_id=school_id,
                suburb_id=property_data.get("suburb_id"),
                name=school_data.get("name", "Unknown School"),
                education_level=school_data.get("educationLevel", "Not Specified"),
                year_range=school_data.get("year", "Not Specified"),
                type=school_data.get("type", "Not Specified"),
                gender=school_data.get("gender", "Unknown"),
            )
            db.add(school)

    def create_property_with_relations(self, db: Session, property_data: Dict[str, Any]) -> Optional[Property]:
        """Create a property with all its related data"""

        if not property_data.get("suburb_id"):
            raise ValueError("suburb_id is required")

        try:
            # Check if property already exists
            listing_id = property_data.get("listingId")
            if listing_id:
                existing_property = db.query(Property).filter(Property.id == listing_id).first()
                if existing_property:
                    print(f"Property with ID {listing_id} already exists, skipping...")
                    return existing_property

            # Transform the raw data
            transformed_data = self.transform_property_data(property_data)

            # Create the main property
            property_create = PropertyCreate(**transformed_data)
            db_property = Property(**property_create.model_dump(exclude_none=True))

            try:
                db.add(db_property)
                db.flush()  # Try to flush to check for conflicts
            except IntegrityError as e:
                db.rollback()
                print(f"IntegrityError for property {transformed_data.get('property_id')}: {str(e)}")
                return None

            # Create schools
            if "schools" in property_data:
                self.create_schools_from_property_data(db, property_data)

            return db_property

        except Exception as e:
            db.rollback()
            raise Exception(f"Error creating property: {str(e)}")


property_import_service = PropertyImportService()
