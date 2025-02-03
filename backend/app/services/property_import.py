import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.property import Property, PropertyEvent, School
from app.schemas.property import PropertyCreate, PropertyEventCreate, SchoolCreate


class PropertyImportService:
    def transform_property_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw JSON data to match our schema structure"""

        return {
            "id": raw_data["listing"]["id"],
            "property_id": raw_data["propertyId"],
            "type": raw_data["type"],
            "category": raw_data["category"],
            "specifications": {
                "bedrooms": raw_data["specifications"]["bedrooms"],
                "bathrooms": raw_data["specifications"]["bathrooms"],
                "parking_spaces": raw_data["specifications"]["parkingSpaces"],
                "internal_area": raw_data["specifications"]["internal_area"],
                "land_area": raw_data["specifications"]["land_area"],
            },
            "address": {
                "display_address": raw_data["address"]["displayAddress"],
                "postcode": raw_data["address"]["postcode"],
                "suburb_name": raw_data["address"]["suburbName"],
                "state": raw_data["address"]["state"],
                "unit_number": raw_data["address"]["unitNumber"],
                "street_number": raw_data["address"]["streetNumber"],
                "street_name": raw_data["address"]["streetName"],
                "street_type": raw_data["address"]["streetType"],
                "latitude": raw_data["address"]["geolocation"]["latitude"],
                "longitude": raw_data["address"]["geolocation"]["longitude"],
            },
            "surrounding_suburbs": raw_data["location"]["surroundingSuburbs"],
            "market_stats": raw_data["marketStats"],
            "listing_url": raw_data["listing"]["url"],
            "listing_status": raw_data["listing"]["status"],
            "listing_type": raw_data["listing"]["type"],
            "display_price": raw_data["listing"]["displayPrice"],
            "images": raw_data["images"],
            "suburb_insights": raw_data["suburbInsights"],
        }

    def create_property_with_relations(self, db: Session, property_data: Dict[str, Any]) -> Property:
        """Create a property with all its related data"""

        # Transform the raw data
        transformed_data = self.transform_property_data(property_data)

        # Create the main property
        property_create = PropertyCreate(**transformed_data)
        db_property = Property(**property_create.model_dump())
        db.add(db_property)
        db.flush()  # Flush to get the ID without committing

        # Create timeline events
        if "timeline" in property_data:
            for event_data in property_data["timeline"]:
                event = PropertyEvent(
                    property_id=db_property.id,
                    event_price=event_data["eventPrice"],
                    event_date=event_data["eventDate"],
                    agency=event_data["agency"],
                    category=event_data["category"],
                    days_on_market=event_data["daysOnMarket"],
                    price_description=event_data["priceDescription"],
                )
                db.add(event)

        # Create schools
        if "schools" in property_data:
            for school_data in property_data["schools"]:
                school = School(
                    property_id=db_property.id,
                    name=school_data["name"],
                    type=school_data["type"],
                    sector=school_data["sector"],
                    gender=school_data["gender"],
                    suburb=school_data["suburb"],
                    distance=school_data["distance"],
                    year_range=school_data["yearRange"],
                )
                db.add(school)

        try:
            db.commit()
            db.refresh(db_property)
            return db_property
        except Exception as e:
            db.rollback()
            raise e

    def import_properties_from_file(self, db: Session, file_path: str) -> List[Property]:
        """Import properties from a JSON file"""

        imported_properties = []

        with open(file_path, "r") as f:
            data = json.load(f)
            properties_data = data["properties"]

            for property_data in properties_data:
                try:
                    imported_property = self.create_property_with_relations(db, property_data)
                    imported_properties.append(imported_property)
                except Exception as e:
                    print(f"Error importing property {property_data.get('propertyId')}: {str(e)}")
                    continue

        return imported_properties


property_import_service = PropertyImportService()
