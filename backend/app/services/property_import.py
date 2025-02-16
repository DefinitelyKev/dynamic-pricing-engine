from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.property import Property, School, property_school
import json

# from app.schemas.property import PropertyCreate, SchoolCreate


class PropertyImportService:
    def transform_property_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw JSON data to match our schema structure"""

        # Get specifications safely
        listing_summary = data.get("listingSummary", {})

        transformed = {
            # Required fields with defaults
            "id": data.get("listingId"),
            "type": data.get("propertyType"),
            "suburb_id": data.get("suburb_id"),
            # Listing Details
            "display_price": data.get("price"),
            "listing_status": listing_summary.get("status"),
            "listing_mode": listing_summary.get("mode"),
            "listing_method": listing_summary.get("method"),
            "listing_url": data.get("listingUrl"),
            # Specifications
            "bedrooms": data.get("beds", 0),
            "bathrooms": data.get("baths", 0),
            "parking_spaces": data.get("parking", 0),
            "land_area": listing_summary.get("stats", 0),
            "features": data.get("features"),
            "structured_features": data.get("structuredFeatures"),
            # Address
            "address": listing_summary.get("address"),
            "unit_number": data.get("unitNumber"),
            "street_number": data.get("streetNumber"),
            "street_name": data.get("street"),
            "suburb_name": data.get("suburb"),
            "postcode": data.get("postcode"),
            "state": data.get("state"),
            # Additional data
            "images": data.get("gallery", []),
        }

        return {k: v for k, v in transformed.items() if v is not None}

    def create_or_get_school(self, db: Session, school_data: Dict[str, Any]) -> Optional[School]:
        school_id = school_data.get("id")
        if not school_id:
            return None

        school_id = int(school_id)

        existing_school = db.query(School).filter(School.id == school_id).first()
        if existing_school:
            return existing_school

        school = School(
            id=school_id,
            name=school_data.get("name"),
            education_level=school_data.get("educationLevel"),
            year_range=school_data.get("year"),
            type=school_data.get("type"),
            gender=school_data.get("gender"),
            state=school_data.get("state"),
            postcode=school_data.get("postCode"),
            suburb_id=school_data.get("suburb_id"),
        )
        try:
            db.add(school)
            db.flush()
            return school
        except IntegrityError:
            db.rollback()
            return None

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
            db_property = Property(**transformed_data)

            try:
                db.add(db_property)
                db.flush()  # Try to flush to check for conflicts
            except IntegrityError as e:
                db.rollback()
                print(f"IntegrityError for property {transformed_data.get('property_id')}: {str(e)}")
                return None

            # Create schools
            if "schools" in property_data:
                for school_data in property_data["schools"]:
                    school_data["suburb_id"] = property_data["suburb_id"]

                    # Create or get school
                    school = self.create_or_get_school(db, school_data)
                    if school:
                        # Create association with distance
                        distance = school_data.get("distance")
                        stmt = property_school.insert().values(
                            property_id=db_property.id, school_id=school.id, distance=distance
                        )
                        db.execute(stmt)

            return db_property

        except Exception as e:
            db.rollback()
            raise Exception(f"Error creating property: {str(e)}")


property_import_service = PropertyImportService()
