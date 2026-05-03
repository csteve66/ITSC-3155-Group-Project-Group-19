from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class AnalyticsSummary(BaseModel):
    start_date: date
    end_date: date
    total_revenue: Decimal = Field(description="Sum of line totals (price × amount) for non-cancelled orders in range.")
    order_count: int
    average_order_value: Decimal = Field(
        description="total_revenue / order_count when order_count > 0, else 0."
    )


class DailyPoint(BaseModel):
    date: date
    revenue: Decimal
    order_count: int


class DailyTrendResponse(BaseModel):
    start_date: date
    end_date: date
    days: list[DailyPoint]


class TopSandwichRow(BaseModel):
    sandwich_id: int
    sandwich_name: str
    units_sold: int
    revenue: Decimal


class TopSandwichesResponse(BaseModel):
    start_date: date
    end_date: date
    limit: int
    items: list[TopSandwichRow]


class OrderTypeRow(BaseModel):
    order_type: str
    order_count: int
    revenue: Decimal


class OrderTypeBreakdownResponse(BaseModel):
    start_date: date
    end_date: date
    items: list[OrderTypeRow]
