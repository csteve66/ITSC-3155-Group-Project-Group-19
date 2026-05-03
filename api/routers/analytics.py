from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..controllers import analytics as controller
from ..schemas import analytics as schema
from ..dependencies.database import get_db

router = APIRouter(
    tags=["Analytics"],
    prefix="/analytics",
)


@router.get("/summary", response_model=schema.AnalyticsSummary)
def get_summary(
    start_date: date | None = Query(
        default=None,
        description="Inclusive start (calendar date). Defaults to 30 days before end_date.",
    ),
    end_date: date | None = Query(
        default=None,
        description="Inclusive end (calendar date). Defaults to today.",
    ),
    db: Session = Depends(get_db),
):
    """Sales totals for non-cancelled orders in the date range (same line math as order history)."""
    return controller.summary(db, start_date=start_date, end_date=end_date)


@router.get("/daily", response_model=schema.DailyTrendResponse)
def get_daily_trend(
    start_date: date | None = Query(
        default=None,
        description="Inclusive start. Defaults to 30 days before end_date.",
    ),
    end_date: date | None = Query(
        default=None,
        description="Inclusive end. Defaults to today.",
    ),
    db: Session = Depends(get_db),
):
    """Revenue and order count per calendar day; missing days are zero-filled."""
    return controller.daily_trend(db, start_date=start_date, end_date=end_date)


@router.get("/top-sandwiches", response_model=schema.TopSandwichesResponse)
def get_top_sandwiches(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Most-ordered sandwiches by units sold (non-cancelled orders)."""
    return controller.top_sandwiches(
        db, start_date=start_date, end_date=end_date, limit=limit
    )


@router.get("/by-order-type", response_model=schema.OrderTypeBreakdownResponse)
def get_by_order_type(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Order counts and revenue split by takeout vs delivery."""
    return controller.by_order_type(db, start_date=start_date, end_date=end_date)
