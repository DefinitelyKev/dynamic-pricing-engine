import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.property import Property, PropertyEvent, School
from app.schemas.property import PropertyCreate, PropertyEventCreate, SchoolCreate


class PropertyImportService:
    def extract_listing_id_from_url(self, url: str) -> Optional[int]:
        """Extract listing ID from the URL"""
        try:
            # Extract the last part of the URL before any query parameters
            url_path = url.split("?")[0]
            # Get the last segment that contains the ID
            last_segment = url_path.rstrip("/").split("-")[-1]
            # Convert to integer
            return int(last_segment)
        except (IndexError, ValueError):
            return None

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
        }

        return {k: v for k, v in transformed.items() if v is not None}

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
                for school_data in property_data["schools"]:
                    school = School(
                        property_id=db_property.id,
                        suburb_id=property_data["suburb_id"],
                        name=school_data.get("name", "Unknown School"),
                        type=school_data.get("type", "Not Specified"),
                        sector=school_data.get("sector", "Not Specified"),
                        gender=school_data.get("gender", "Unknown"),
                        distance=school_data.get("distance", 0.0),
                        year_range=school_data.get("yearRange", "Not Specified"),
                    )
                    db.add(school)

            return db_property

        except Exception as e:
            db.rollback()
            raise Exception(f"Error creating property: {str(e)}")


property_import_service = PropertyImportService()
