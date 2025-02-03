from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.models.property import Property, PropertyEvent, School
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyEventCreate, SchoolCreate
from .base import BaseService
from datetime import datetime


class PropertyService(BaseService[Property, PropertyCreate, PropertyUpdate]):
    def __init__(self):
        super().__init__(Property)

    def update_display_price(
        self, db: Session, *, property_id: int, new_price: str, category: str = "Update", agency: Optional[str] = None
    ) -> Optional[Property]:
        """
        Update property display price and create a timeline event
        """
        property = self.get(db, property_id)
        if property:
            # Update display price
            property.display_price = new_price

            # Add timeline event
            event = PropertyEvent(
                property_id=property_id,
                event_price=float(new_price) if new_price.replace(".", "").isdigit() else 0.0,
                event_date=datetime.now().isoformat(),
                agency=agency,
                category=category,
                days_on_market=0,
                price_description="PRICE UPDATE",
            )
            db.add(event)

            db.commit()
            db.refresh(property)
            return property
        return None

    def get_timeline(self, db: Session, *, property_id: int, skip: int = 0, limit: int = 100) -> List[PropertyEvent]:
        """
        Get property timeline events
        """
        return (
            db.query(PropertyEvent)
            .filter(PropertyEvent.property_id == property_id)
            .order_by(PropertyEvent.event_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_market_stats(self, db: Session, *, property_id: int, market_stats: Dict) -> Optional[Property]:
        """
        Update property market statistics
        """
        property = self.get(db, property_id)
        if property:
            property.market_stats = market_stats
            db.commit()
            db.refresh(property)
            return property
        return None

    def update_suburb_insights(self, db: Session, *, property_id: int, suburb_insights: Dict) -> Optional[Property]:
        """
        Update property suburb insights
        """
        property = self.get(db, property_id)
        if property:
            property.suburb_insights = suburb_insights
            db.commit()
            db.refresh(property)
            return property
        return None

    def add_school(self, db: Session, *, property_id: int, school_data: SchoolCreate) -> Optional[School]:
        """
        Add a new school to property
        """
        property = self.get(db, property_id)
        if not property:
            return None

        school = School(property_id=property_id, **school_data.model_dump(exclude={"property_id"}))
        db.add(school)

        try:
            db.commit()
            db.refresh(school)
            return school
        except Exception as e:
            db.rollback()
            raise e

    def get_schools(self, db: Session, *, property_id: int, skip: int = 0, limit: int = 100) -> List[School]:
        """
        Get schools associated with a property
        """
        return db.query(School).filter(School.property_id == property_id).offset(skip).limit(limit).all()

    def search_properties(
        self,
        db: Session,
        *,
        suburb: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        bedrooms: Optional[int] = None,
        property_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Property]:
        """
        Search properties with filters
        """
        query = db.query(Property)

        if suburb:
            query = query.filter(Property.suburb_name.ilike(f"%{suburb}%"))
        if property_type:
            query = query.filter(Property.type == property_type)
        if bedrooms:
            query = query.filter(Property.bedrooms >= bedrooms)
        # Price filtering will need to be handled differently since we now store display_price as string
        # You might want to add a numeric_price field to the model if exact price filtering is needed

        return query.offset(skip).limit(limit).all()

    def get_nearby_properties(
        self, db: Session, *, property_id: int, radius_km: float = 5.0, limit: int = 10
    ) -> List[Property]:
        """
        Get properties within a radius using geolocation
        """
        property = self.get(db, property_id)
        if not property or not property.latitude or not property.longitude:
            return []

        # Approximate distance calculation using the Haversine formula
        from sqlalchemy import func
        from math import radians

        lat = radians(property.latitude)
        lng = radians(property.longitude)
        radius_earth = 6371  # Earth's radius in kilometers

        return (
            db.query(Property)
            .filter(Property.id != property_id)
            .filter(
                func.acos(
                    func.sin(lat) * func.sin(func.radians(Property.latitude))
                    + func.cos(lat)
                    * func.cos(func.radians(Property.latitude))
                    * func.cos(func.radians(Property.longitude) - lng)
                )
                * radius_earth
                <= radius_km
            )
            .limit(limit)
            .all()
        )


property_service = PropertyService()
