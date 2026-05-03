from datetime import date, datetime, time, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..models import orders as order_model
from ..models import order_details as detail_model
from ..models import sandwiches as sandwich_model


def _resolve_date_range(
    start_date: date | None,
    end_date: date | None,
) -> tuple[datetime, datetime, date, date]:
    end_d = end_date or date.today()
    start_d = start_date or (end_d - timedelta(days=30))
    if start_d > end_d:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be on or before end_date",
        )
    start_dt = datetime.combine(start_d, time.min)
    end_dt = datetime.combine(end_d + timedelta(days=1), time.min)
    return start_dt, end_dt, start_d, end_d


def _order_filters(start_dt: datetime, end_dt: datetime):
    return (
        order_model.Order.order_date >= start_dt,
        order_model.Order.order_date < end_dt,
        order_model.Order.order_status != "cancelled",
    )


def _line_revenue_expression():
    return func.coalesce(
        sandwich_model.Sandwich.price * detail_model.OrderDetail.amount,
        0,
    )


def summary(db: Session, start_date: date | None, end_date: date | None):
    start_dt, end_dt, start_d, end_d = _resolve_date_range(start_date, end_date)
    filters = _order_filters(start_dt, end_dt)
    try:
        order_count = (
            db.query(func.count(order_model.Order.id))
            .filter(*filters)
            .scalar()
        ) or 0

        total_revenue = (
            db.query(func.coalesce(func.sum(_line_revenue_expression()), 0))
            .select_from(order_model.Order)
            .outerjoin(
                detail_model.OrderDetail,
                detail_model.OrderDetail.order_id == order_model.Order.id,
            )
            .outerjoin(
                sandwich_model.Sandwich,
                sandwich_model.Sandwich.id == detail_model.OrderDetail.sandwich_id,
            )
            .filter(*filters)
            .scalar()
        )
        total_revenue = Decimal(str(total_revenue or 0))
        avg = (
            (total_revenue / Decimal(order_count)).quantize(Decimal("0.01"))
            if order_count
            else Decimal("0.00")
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.__dict__.get("orig", e)),
        ) from e

    return {
        "start_date": start_d,
        "end_date": end_d,
        "total_revenue": total_revenue,
        "order_count": int(order_count),
        "average_order_value": avg,
    }


def daily_trend(db: Session, start_date: date | None, end_date: date | None):
    start_dt, end_dt, start_d, end_d = _resolve_date_range(start_date, end_date)
    filters = _order_filters(start_dt, end_dt)
    try:
        rows = (
            db.query(
                func.date(order_model.Order.order_date).label("day"),
                func.coalesce(func.sum(_line_revenue_expression()), 0).label("revenue"),
                func.count(func.distinct(order_model.Order.id)).label("order_count"),
            )
            .select_from(order_model.Order)
            .outerjoin(
                detail_model.OrderDetail,
                detail_model.OrderDetail.order_id == order_model.Order.id,
            )
            .outerjoin(
                sandwich_model.Sandwich,
                sandwich_model.Sandwich.id == detail_model.OrderDetail.sandwich_id,
            )
            .filter(*filters)
            .group_by(func.date(order_model.Order.order_date))
            .order_by(func.date(order_model.Order.order_date))
            .all()
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.__dict__.get("orig", e)),
        ) from e

    by_day = {}
    for day, revenue, oc in rows:
        if day is None:
            continue
        if isinstance(day, date):
            d = day
        elif isinstance(day, str):
            d = date.fromisoformat(day[:10])
        else:
            d = datetime.combine(day, time.min).date()
        by_day[d] = {
            "revenue": Decimal(str(revenue or 0)),
            "order_count": int(oc or 0),
        }

    days_out: list[dict] = []
    cur = start_d
    while cur <= end_d:
        data = by_day.get(cur, {"revenue": Decimal("0.00"), "order_count": 0})
        days_out.append(
            {
                "date": cur,
                "revenue": data["revenue"],
                "order_count": data["order_count"],
            }
        )
        cur += timedelta(days=1)

    return {"start_date": start_d, "end_date": end_d, "days": days_out}


def top_sandwiches(db: Session, start_date: date | None, end_date: date | None, limit: int):
    start_dt, end_dt, start_d, end_d = _resolve_date_range(start_date, end_date)
    filters = _order_filters(start_dt, end_dt)
    lim = max(1, min(limit, 50))
    try:
        rows = (
            db.query(
                sandwich_model.Sandwich.id,
                sandwich_model.Sandwich.sandwich_name,
                func.sum(detail_model.OrderDetail.amount).label("units_sold"),
                func.coalesce(
                    func.sum(_line_revenue_expression()),
                    0,
                ).label("revenue"),
            )
            .select_from(detail_model.OrderDetail)
            .join(
                order_model.Order,
                order_model.Order.id == detail_model.OrderDetail.order_id,
            )
            .join(
                sandwich_model.Sandwich,
                sandwich_model.Sandwich.id == detail_model.OrderDetail.sandwich_id,
            )
            .filter(*filters)
            .group_by(
                sandwich_model.Sandwich.id,
                sandwich_model.Sandwich.sandwich_name,
            )
            .order_by(func.sum(detail_model.OrderDetail.amount).desc())
            .limit(lim)
            .all()
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.__dict__.get("orig", e)),
        ) from e

    items = [
        {
            "sandwich_id": sid,
            "sandwich_name": name or "",
            "units_sold": int(units or 0),
            "revenue": Decimal(str(rev or 0)),
        }
        for sid, name, units, rev in rows
    ]
    return {"start_date": start_d, "end_date": end_d, "limit": lim, "items": items}


def by_order_type(db: Session, start_date: date | None, end_date: date | None):
    start_dt, end_dt, start_d, end_d = _resolve_date_range(start_date, end_date)
    filters = _order_filters(start_dt, end_dt)
    try:
        rows = (
            db.query(
                order_model.Order.order_type,
                func.count(func.distinct(order_model.Order.id)).label("order_count"),
                func.coalesce(func.sum(_line_revenue_expression()), 0).label("revenue"),
            )
            .select_from(order_model.Order)
            .outerjoin(
                detail_model.OrderDetail,
                detail_model.OrderDetail.order_id == order_model.Order.id,
            )
            .outerjoin(
                sandwich_model.Sandwich,
                sandwich_model.Sandwich.id == detail_model.OrderDetail.sandwich_id,
            )
            .filter(*filters)
            .group_by(order_model.Order.order_type)
            .all()
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e.__dict__.get("orig", e)),
        ) from e

    items = [
        {
            "order_type": ot or "unknown",
            "order_count": int(oc or 0),
            "revenue": Decimal(str(rev or 0)),
        }
        for ot, oc, rev in rows
    ]
    return {"start_date": start_d, "end_date": end_d, "items": items}
