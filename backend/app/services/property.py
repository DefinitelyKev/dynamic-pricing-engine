from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.models.property import Property, School
from app.schemas.property import PropertyCreate, PropertyUpdate, SchoolCreate
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
            db.commit()
            db.refresh(property)
            return property
        return None

    def update_suburb_insights(self, db: Session, *, property_id: int, suburb_insights: Dict) -> Optional[Property]:
        """
        Update property suburb insights
        """
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

    # def get_schools(self, db: Session, *, property_id: int, skip: int = 0, limit: int = 100) -> List[School]:
    #     """
    #     Get schools associated with a property
    #     """
    #     return db.query(School).filter(School.property_id == property_id).offset(skip).limit(limit).all()

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


property_service = PropertyService()
