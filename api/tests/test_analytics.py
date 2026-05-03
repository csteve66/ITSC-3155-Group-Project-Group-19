from datetime import date, datetime, timedelta
from decimal import Decimal

from ..models.orders import Order
from ..models.order_details import OrderDetail
from ..models.sandwiches import Sandwich


def _seed_orders(db):
    s1 = Sandwich(sandwich_name="Alpha", price=Decimal("5.00"), calories=100, category="Classic")
    s2 = Sandwich(sandwich_name="Beta", price=Decimal("10.00"), calories=200, category="Premium")
    db.add_all([s1, s2])
    db.commit()
    db.refresh(s1)
    db.refresh(s2)

    today = date.today()
    d0 = datetime.combine(today, datetime.min.time())
    d_prev = datetime.combine(today - timedelta(days=1), datetime.min.time())

    o1 = Order(
        customer_name="A",
        order_type="takeout",
        order_date=d0,
        description="",
        tracking_number="T-001",
        order_status="completed",
        status_updated_at=d0,
    )
    o2 = Order(
        customer_name="B",
        order_type="delivery",
        customer_address="1 Main",
        order_date=d_prev,
        description="",
        tracking_number="T-002",
        order_status="completed",
        status_updated_at=d_prev,
    )
    o3 = Order(
        customer_name="C",
        order_type="takeout",
        order_date=d0,
        description="",
        tracking_number="T-003",
        order_status="cancelled",
        status_updated_at=d0,
    )
    db.add_all([o1, o2, o3])
    db.commit()
    db.refresh(o1)
    db.refresh(o2)
    db.refresh(o3)

    db.add_all(
        [
            OrderDetail(order_id=o1.id, sandwich_id=s1.id, amount=2),
            OrderDetail(order_id=o1.id, sandwich_id=s2.id, amount=1),
            OrderDetail(order_id=o2.id, sandwich_id=s2.id, amount=3),
            OrderDetail(order_id=o3.id, sandwich_id=s1.id, amount=99),
        ]
    )
    db.commit()


def test_analytics_summary_excludes_cancelled_and_matches_revenue(client, test_db_session):
    _seed_orders(test_db_session)
    r = client.get("/analytics/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["order_count"] == 2
    # o1: 2*5 + 1*10 = 20; o2: 3*10 = 30; cancelled o3 ignored
    assert Decimal(data["total_revenue"]) == Decimal("50.00")
    assert Decimal(data["average_order_value"]) == Decimal("25.00")


def test_analytics_daily_zero_fill(client, test_db_session):
    _seed_orders(test_db_session)
    today = date.today()
    start = (today - timedelta(days=2)).isoformat()
    end = today.isoformat()
    r = client.get("/analytics/daily", params={"start_date": start, "end_date": end})
    assert r.status_code == 200
    data = r.json()
    days = {row["date"]: row for row in data["days"]}
    assert days[today.isoformat()]["order_count"] == 1
    assert Decimal(days[today.isoformat()]["revenue"]) == Decimal("20.00")
    assert days[(today - timedelta(days=1)).isoformat()]["order_count"] == 1
    assert Decimal(days[(today - timedelta(days=1)).isoformat()]["revenue"]) == Decimal("30.00")
    assert days[(today - timedelta(days=2)).isoformat()]["order_count"] == 0
    assert Decimal(days[(today - timedelta(days=2)).isoformat()]["revenue"]) == Decimal("0")


def test_top_sandwiches_ordering(client, test_db_session):
    _seed_orders(test_db_session)
    r = client.get("/analytics/top-sandwiches", params={"limit": 5})
    assert r.status_code == 200
    items = r.json()["items"]
    assert items[0]["sandwich_name"] == "Beta"
    assert items[0]["units_sold"] == 4
    assert items[1]["sandwich_name"] == "Alpha"
    assert items[1]["units_sold"] == 2


def test_by_order_type(client, test_db_session):
    _seed_orders(test_db_session)
    r = client.get("/analytics/by-order-type")
    assert r.status_code == 200
    by_type = {row["order_type"]: row for row in r.json()["items"]}
    assert by_type["takeout"]["order_count"] == 1
    assert by_type["delivery"]["order_count"] == 1
    assert Decimal(by_type["takeout"]["revenue"]) == Decimal("20.00")
    assert Decimal(by_type["delivery"]["revenue"]) == Decimal("30.00")


def test_summary_rejects_inverted_range(client, test_db_session):
    _seed_orders(test_db_session)
    r = client.get(
        "/analytics/summary",
        params={"start_date": "2099-01-01", "end_date": "2020-01-01"},
    )
    assert r.status_code == 400
