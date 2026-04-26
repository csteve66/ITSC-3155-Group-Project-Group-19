from . import customers, orders, order_details, recipes, sandwiches, resources, promotions, payments, reviews
from sqlalchemy import inspect, text

from ..dependencies.database import engine


def _sync_orders_columns():
    inspector = inspect(engine)
    existing_columns = {column["name"] for column in inspector.get_columns("orders")}
    existing_indexes = {index["name"] for index in inspector.get_indexes("orders")}
    statements = []

    if "tracking_number" not in existing_columns:
        statements.append(
            "ALTER TABLE orders ADD COLUMN tracking_number VARCHAR(64) NULL"
        )
    if "order_status" not in existing_columns:
        statements.append(
            "ALTER TABLE orders ADD COLUMN order_status VARCHAR(32) NOT NULL DEFAULT 'pending'"
        )
    if "status_updated_at" not in existing_columns:
        statements.append(
            "ALTER TABLE orders ADD COLUMN status_updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP"
        )

    if statements:
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))
            # Backfill and enforce constraints once columns exist.
            connection.execute(
                text(
                    "UPDATE orders SET tracking_number = CONCAT('ORD-', LPAD(id, 8, '0')) "
                    "WHERE tracking_number IS NULL OR tracking_number = ''"
                )
            )
            connection.execute(
                text(
                    "UPDATE orders SET status_updated_at = COALESCE(status_updated_at, NOW())"
                )
            )
            connection.execute(
                text(
                    "ALTER TABLE orders MODIFY COLUMN tracking_number VARCHAR(64) NOT NULL"
                )
            )
            if "uq_orders_tracking_number" not in existing_indexes:
                connection.execute(
                    text(
                        "ALTER TABLE orders ADD UNIQUE INDEX uq_orders_tracking_number (tracking_number)"
                    )
                )


def index():
    customers.Base.metadata.create_all(engine)
    orders.Base.metadata.create_all(engine)
    _sync_orders_columns()
    order_details.Base.metadata.create_all(engine)
    recipes.Base.metadata.create_all(engine)
    sandwiches.Base.metadata.create_all(engine)
    resources.Base.metadata.create_all(engine)
    promotions.Base.metadata.create_all(engine)
    payments.Base.metadata.create_all(engine)
    reviews.Base.metadata.create_all(engine)
