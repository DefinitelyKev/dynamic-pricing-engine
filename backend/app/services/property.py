from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.property import Property, PriceHistory, MarketData
from app.schemas.property import PropertyCreate, PropertyUpdate, PriceHistoryCreate, MarketDataCreate
from .base import BaseService


class PropertyService(BaseService[Property, PropertyCreate, PropertyUpdate]):
    def __init__(self):
        super().__init__(Property)

    def update_price(self, db: Session, *, property_id: int, new_price: float, reason: str) -> Optional[Property]:
        property = self.get(db, property_id)
        if property:
            # Update current price
            property.current_price = new_price

            # Add price history
            price_history = PriceHistory(property_id=property_id, price=new_price, reason=reason)
            db.add(price_history)

            db.commit()
            db.refresh(property)
            return property
        return None

    def get_price_history(
        self, db: Session, *, property_id: int, skip: int = 0, limit: int = 100
    ) -> List[PriceHistory]:
        return db.query(PriceHistory).filter(PriceHistory.property_id == property_id).offset(skip).limit(limit).all()

    def update_market_data(
        self, db: Session, *, property_id: int, market_data: MarketDataCreate
    ) -> Optional[MarketData]:
        db_market_data = db.query(MarketData).filter(MarketData.property_id == property_id).first()

        if db_market_data:
            # Update existing market data
            for field, value in market_data.model_dump().items():
                setattr(db_market_data, field, value)
        else:
            # Create new market data
            db_market_data = MarketData(**market_data.model_dump())
            db.add(db_market_data)

        db.commit()
        db.refresh(db_market_data)
        return db_market_data


property_service = PropertyService()
