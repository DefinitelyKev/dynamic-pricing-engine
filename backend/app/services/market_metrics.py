from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract, case, text, TIMESTAMP
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from app.models import Property, PropertyEvent, Suburb
from app.schemas.market_metrics import SuburbMetrics, PriceHistory, PropertyStats, SuburbPerformance, MarketSummary


class MarketMetricsService:
    @staticmethod
    def calculate_price_growth(prices: List[float]) -> float:
        """Calculate percentage growth between first and last price"""
        if not prices or len(prices) < 2:
            return 0.0
        return ((prices[-1] - prices[0]) / prices[0]) * 100

    @staticmethod
    def parse_price_string(price_str: str) -> Optional[float]:
        """Convert price string to float"""
        try:
            # Remove currency symbols and commas
            cleaned = price_str.replace("$", "").replace(",", "").strip()
            return float(cleaned)
        except (ValueError, AttributeError):
            return None

    def get_suburb_metrics(self, db: Session, suburb_id: int) -> Optional[SuburbMetrics]:
        """Get comprehensive metrics for a suburb"""
        suburb = db.query(Suburb).filter(Suburb.id == suburb_id).first()
        if not suburb:
            return None

        # Get recent property events
        three_months_ago = datetime.now() - timedelta(days=90)
        recent_events = (
            db.query(PropertyEvent)
            .join(Property)
            .filter(Property.suburb_id == suburb_id, PropertyEvent.event_date >= three_months_ago.strftime("%Y-%m-%d"))
            .order_by(PropertyEvent.event_date)
            .all()
        )

        # Calculate price growth
        prices = [event.event_price for event in recent_events]
        price_growth = self.calculate_price_growth(prices)

        return SuburbMetrics(
            median_price=suburb.median_price or 0.0,
            inventory=suburb.properties_for_sale,
            avg_days_on_market=suburb.avg_days_on_market or 0.0,
            price_growth=round(price_growth, 1),
        )

    def get_monthly_stats(self, db: Session, suburb_id: int, months: int = 6) -> List[PropertyStats]:
        """Get monthly property statistics"""
        start_date = datetime.now() - timedelta(days=30 * months)

        # Using PostgreSQL's date casting and date_trunc
        stats = (
            db.query(
                func.date_trunc("month", func.cast(PropertyEvent.event_date, TIMESTAMP)).label("month"),
                func.avg(PropertyEvent.event_price).label("avg_price"),
                func.count(Property.id.distinct()).label("inventory"),
            )
            .join(Property)
            .filter(Property.suburb_id == suburb_id, PropertyEvent.event_date >= start_date.strftime("%Y-%m-%d"))
            .group_by(text("month"))
            .order_by(text("month"))
            .all()
        )

        return [
            PropertyStats(
                month=stat[0].strftime("%b") if stat[0] else "Unknown",
                avg_price=round(stat[1] or 0, 2),
                inventory=stat[2],
            )
            for stat in stats
        ]

    def get_price_history(self, db: Session, suburb_id: int, months: int = 6) -> List[PriceHistory]:
        """Get price history with month-over-month changes"""
        stats = self.get_monthly_stats(db, suburb_id, months)

        price_history = []
        for i in range(1, len(stats)):
            prev_price = stats[i - 1].avg_price
            curr_price = stats[i].avg_price
            if prev_price > 0:  # Avoid division by zero
                price_change = ((curr_price - prev_price) / prev_price) * 100
                price_history.append(PriceHistory(date=stats[i].month, price_change=round(price_change, 1)))

        return price_history

    def get_top_suburbs(self, db: Session, limit: int = 10) -> List[SuburbPerformance]:
        """Get top performing suburbs"""
        query_results = (
            db.query(
                Suburb.name,
                Suburb.median_price,
                Suburb.avg_days_on_market,
                (
                    case(
                        (
                            (Suburb.properties_for_sale + Suburb.properties_for_rent) > 0,
                            Suburb.properties_for_sale
                            * 100.0
                            / (Suburb.properties_for_sale + Suburb.properties_for_rent),
                        ),
                        else_=0,
                    )
                ).label("sales_ratio"),
            )
            .filter(Suburb.median_price.isnot(None))
            .order_by(Suburb.median_price.desc())
            .limit(limit)
            .all()
        )

        return [
            SuburbPerformance(
                name=row[0],
                median_price=float(row[1]) if row[1] is not None else 0.0,
                avg_days_on_market=float(row[2]) if row[2] is not None else 0.0,
                sales_ratio=float(row[3]) if row[3] is not None else 0.0,
            )
            for row in query_results
        ]

    def get_market_summary(self, db: Session) -> MarketSummary:
        """Get overall market summary"""
        total_properties = db.query(func.count(Property.id)).scalar() or 0

        # Calculate average price from display_price strings
        properties = db.query(Property.display_price).all()
        prices = [self.parse_price_string(p[0]) for p in properties if p[0] is not None]
        avg_price = sum(p for p in prices if p is not None) / len(prices) if prices else 0

        active_listings = db.query(func.count(Property.id)).filter(Property.listing_status == "Active").scalar() or 0

        return MarketSummary(
            total_properties=total_properties,
            average_price=round(avg_price, 2),
            active_listings=active_listings,
            updated_at=datetime.now(),
        )

    def compare_suburbs(self, db: Session, suburb_ids: List[int]) -> Dict[int, SuburbMetrics]:
        """Compare metrics for multiple suburbs"""
        metrics = {}
        for suburb_id in suburb_ids:
            suburb_metrics = self.get_suburb_metrics(db, suburb_id)
            if suburb_metrics:
                metrics[suburb_id] = suburb_metrics
        return metrics


market_metrics_service = MarketMetricsService()
