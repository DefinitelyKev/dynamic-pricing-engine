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

    def transform_property_data(self, raw_data: Dict[str, Any], suburb_id: int) -> Dict[str, Any]:
        """Transform raw JSON data to match our schema structure"""

        # Get specifications safely
        specs = raw_data.get("specifications", {})
        # Get address safely
        address = raw_data.get("address", {})
        # Get listing safely with defaults
        listing = raw_data.get("listing", {})

        # Get listing URL and ID from original_listing_url if not in listing object
        original_url = raw_data.get("original_listing_url")
        listing_url = listing.get("url")
        listing_id = listing.get("id")

        if original_url:
            if not listing_url:
                listing_url = original_url
            if not listing_id:
                listing_id = self.extract_listing_id_from_url(original_url)

        transformed = {
            # Required fields with defaults
            "id": (
                listing_id or self.extract_listing_id_from_url(listing_url)
                if listing_url
                else int(raw_data["propertyId"].replace("-", ""))
            ),
            "property_id": raw_data.get("propertyId", "UNKNOWN"),
            "type": raw_data.get("type", "Unknown"),
            "category": raw_data.get("category", "Unknown"),
            "suburb_id": suburb_id,
            # Specifications
            "bedrooms": specs.get("bedrooms"),
            "bathrooms": specs.get("bathrooms"),
            "parking_spaces": specs.get("parkingSpaces"),
            "internal_area": specs.get("internal_area"),
            "land_area": specs.get("land_area"),
            # Address
            "display_address": address.get("displayAddress", "No address provided"),
            "postcode": address.get("postcode", ""),
            "suburb_name": address.get("suburbName", ""),
            "state": address.get("state", ""),
            "unit_number": address.get("unitNumber"),
            "street_number": address.get("streetNumber", ""),
            "street_name": address.get("streetName", ""),
            "street_type": address.get("streetType", ""),
            "latitude": address.get("geolocation", {}).get("latitude"),
            "longitude": address.get("geolocation", {}).get("longitude"),
            # Location details
            "region": raw_data.get("location", {}).get("suburb", {}).get("region"),
            "area": raw_data.get("location", {}).get("suburb", {}).get("area"),
            # Required listing fields with defaults
            "listing_url": listing_url
            or original_url
            or f"https://example.com/property/{raw_data.get('propertyId', 'unknown')}",
            "listing_status": listing.get("status") or "UNKNOWN",
            "listing_type": listing.get("type") or "UNKNOWN",
            "display_price": listing.get("displayPrice") or "Price not provided",
            # Additional data
            "market_stats": raw_data.get("marketStats", {}),
            "images": raw_data.get("images", []),
            "suburb_insights": raw_data.get("suburbInsights", {}),
        }

        return {k: v for k, v in transformed.items() if v is not None}

    def create_property_with_relations(self, db: Session, property_data: Dict[str, Any]) -> Optional[Property]:
        """Create a property with all its related data"""

        if not property_data.get("suburb_id"):
            raise ValueError("suburb_id is required")

        try:
            # Check if property already exists
            listing_id = property_data.get("listing", {}).get("id")
            if listing_id:
                existing_property = db.query(Property).filter(Property.id == listing_id).first()
                if existing_property:
                    print(f"Property with ID {listing_id} already exists, skipping...")
                    return existing_property

            # Transform the raw data
            transformed_data = self.transform_property_data(property_data, property_data["suburb_id"])

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

            # Create timeline events
            if "timeline" in property_data:
                for event_data in property_data["timeline"]:
                    try:
                        event_price = float(str(event_data.get("eventPrice", "0")).replace(",", ""))
                    except (ValueError, TypeError):
                        event_price = 0.0

                    event = PropertyEvent(
                        property_id=db_property.id,
                        event_price=event_price,
                        event_date=event_data.get("eventDate", ""),
                        agency=event_data.get("agency"),
                        category=event_data.get("category", ""),
                        days_on_market=event_data.get("daysOnMarket", 0),
                        price_description=event_data.get("priceDescription", ""),
                    )
                    db.add(event)

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
