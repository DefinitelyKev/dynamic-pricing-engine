from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from app.core.database import get_db
from app.services.market_metrics import market_metrics_service
from app.schemas.market_metrics import SuburbMetrics, PriceHistory, PropertyStats, SuburbPerformance, MarketSummary

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/suburb/{suburb_id}", response_model=SuburbMetrics)
async def get_suburb_metrics(suburb_id: int, db: Session = Depends(get_db)) -> SuburbMetrics:
    """Get key metrics for a specific suburb"""
    metrics = market_metrics_service.get_suburb_metrics(db, suburb_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Suburb not found")
    return metrics


@router.get("/price-history/{suburb_id}", response_model=List[PriceHistory])
async def get_price_history(suburb_id: int, db: Session = Depends(get_db)) -> List[PriceHistory]:
    """Get monthly price changes for a suburb"""
    suburb_exists = market_metrics_service.get_suburb_metrics(db, suburb_id)
    if not suburb_exists:
        raise HTTPException(status_code=404, detail="Suburb not found")

    return market_metrics_service.get_price_history(db, suburb_id)


@router.get("/property-stats/{suburb_id}", response_model=List[PropertyStats])
async def get_property_stats(suburb_id: int, db: Session = Depends(get_db)) -> List[PropertyStats]:
    """Get monthly property statistics for a suburb"""
    suburb_exists = market_metrics_service.get_suburb_metrics(db, suburb_id)
    if not suburb_exists:
        raise HTTPException(status_code=404, detail="Suburb not found")

    return market_metrics_service.get_monthly_stats(db, suburb_id)


@router.get("/top-suburbs", response_model=List[SuburbPerformance])
async def get_top_performing_suburbs(limit: int = 10, db: Session = Depends(get_db)) -> List[SuburbPerformance]:
    """Get top performing suburbs by price growth"""
    return market_metrics_service.get_top_suburbs(db, limit)


@router.get("/market-summary", response_model=MarketSummary)
async def get_market_summary(db: Session = Depends(get_db)) -> MarketSummary:
    """Get overall market summary statistics"""
    return market_metrics_service.get_market_summary(db)


# Optional: Add endpoint for getting metrics for multiple suburbs
@router.get("/suburbs/compare", response_model=Dict[int, SuburbMetrics])
async def compare_suburbs(suburb_ids: List[int], db: Session = Depends(get_db)) -> Dict[int, SuburbMetrics]:
    """Compare metrics for multiple suburbs"""
    if len(suburb_ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 suburbs can be compared at once")

    metrics = {}
    for suburb_id in suburb_ids:
        suburb_metrics = market_metrics_service.get_suburb_metrics(db, suburb_id)
        if suburb_metrics:
            metrics[suburb_id] = suburb_metrics

    if not metrics:
        raise HTTPException(status_code=404, detail="No valid suburbs found")

    return metrics
