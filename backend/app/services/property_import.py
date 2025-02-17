from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.property import Property, School, property_school
from app.models.suburb import Suburb


class PropertyImportService:
    def transform_property_data(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw JSON data to match our schema structure"""

        listing_summary = property_data.get("listingSummary", {})

        transformed = {
            # Required fields with defaults
            "id": property_data.get("listingId"),
            "type": property_data.get("propertyType"),
            "suburb_id": property_data.get("suburb_id"),
            # Listing Details
            "display_price": property_data.get("price"),
            "listing_status": listing_summary.get("status"),
            "listing_mode": listing_summary.get("mode"),
            "listing_method": listing_summary.get("method"),
            "listing_url": property_data.get("listingUrl"),
            # Specifications
            "bedrooms": property_data.get("beds", 0),
            "bathrooms": property_data.get("baths", 0),
            "parking_spaces": property_data.get("parking", 0),
            "land_area": listing_summary.get("stats", 0),
            "features": property_data.get("features"),
            "structured_features": property_data.get("structuredFeatures"),
            # Address
            "address": listing_summary.get("address"),
            "unit_number": property_data.get("unitNumber"),
            "street_number": property_data.get("streetNumber"),
            "street_name": property_data.get("street"),
            "suburb_name": property_data.get("suburb"),
            "postcode": property_data.get("postcode"),
            "state": property_data.get("state"),
            # Additional data
            "images": property_data.get("gallery", []),
        }

        return {k: v for k, v in transformed.items() if v is not None}

    def create_or_get_school(self, db: Session, school_data: Dict[str, Any]) -> Optional[School]:
        school_id = school_data.get("id")
        if not school_id:
            return None

        # Check if school exists in database
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
        except IntegrityError:
            db.rollback()
            return None

        return school

    def create_or_get_suburb(self, db: Session, property_data: Dict[str, Any]) -> Optional[Suburb]:
        """Create a suburb if it doesn't exist and return it"""

        # Extract suburb data from property
        suburb_name = property_data.get("suburb")
        suburb_postcode = property_data.get("postcode")
        if not suburb_name or not suburb_postcode:
            raise ValueError("Missing required suburb information (name or postcode)")

        suburb_insights = property_data.get("suburbInsights", {})
        if not suburb_insights:
            raise ValueError("No suburb information found in property data")

        # Check if suburb exists in database
        suburb = db.query(Suburb).filter_by(name=suburb_name, postcode=suburb_postcode).first()
        if suburb:
            return suburb

        suburb_insights = property_data.get("suburbInsights", {})
        demographics = suburb_insights.get("demographics", {})

        # Create new suburb
        suburb = Suburb(
            name=suburb_name,
            postcode=suburb_postcode,
            state=property_data.get("state"),
            suburb_profile_url=suburb_insights.get("suburbProfileUrl"),
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

        try:
            db.add(suburb)
            db.flush()
        except IntegrityError as e:
            db.rollback()
            return None

        return suburb

    def create_property_with_relations(self, db: Session, property_data: Dict[str, Any]) -> Optional[Property]:
        """Create a property with all its related data"""

        if not property_data.get("suburb_id"):
            raise ValueError("suburb_id is required")

        if not property_data.get("listingId"):
            raise ValueError("no listingId for property")

        try:
            # Check if property already exists
            listing_id = property_data.get("listingId")
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
                db.flush()
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
