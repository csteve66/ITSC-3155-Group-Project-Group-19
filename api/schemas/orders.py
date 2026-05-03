from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from .order_details import OrderDetail



class OrderBase(BaseModel):
    customer_name: str
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    description: Optional[str] = None
    order_type: str = Field(default='takeout', pattern='^(takeout|delivery)$')


class OrderCreate(OrderBase):
    promo_code: Optional[str] = None


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    description: Optional[str] = None
    order_status: Optional[str] = None
    order_type: Optional[str] = Field(default=None, pattern='^(takeout|delivery)$')


class OrderStatusUpdate(BaseModel):
    actor_role: str = Field(pattern='^(staff|cook)$')
    order_status: str = Field(
        pattern='^(pending|preparing|ready_for_pickup|out_for_delivery|completed|cancelled)$'
    )


class OrderHistoryRecord(BaseModel):
    id: int
    tracking_number: str
    status: str
    order_type: str
    total_price: Decimal
    order_date: Optional[datetime] = None

    class ConfigDict:
        from_attributes = True


class Order(OrderBase):
    id: int
    order_date: Optional[datetime] = None
    tracking_number: str
    order_status: str
    status_updated_at: Optional[datetime] = None
    order_details: list[OrderDetail] = None

    class ConfigDict:
        from_attributes = True


class KitchenItem(BaseModel):
    sandwich_name: str
    quantity: int

    class ConfigDict:
        from_attributes = True


class KitchenOrder(BaseModel):
    id: int
    tracking_number: str
    order_status: str
    order_type: str
    order_date: Optional[datetime] = None
    items: list[KitchenItem] = []

    class ConfigDict:
        from_attributes = True
