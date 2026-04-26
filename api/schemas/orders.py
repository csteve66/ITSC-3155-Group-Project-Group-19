from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .order_details import OrderDetail



class OrderBase(BaseModel):
    customer_name: str
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    description: Optional[str] = None
    order_type: str = Field(default='takeout', pattern='^(takeout|delivery)$')


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    description: Optional[str] = None
    order_status: Optional[str] = None
    order_type: Optional[str] = Field(default=None, pattern='^(takeout|delivery)$')


class OrderStatusUpdate(BaseModel):
    order_status: str


class Order(OrderBase):
    id: int
    order_date: Optional[datetime] = None
    tracking_number: str
    order_status: str
    status_updated_at: Optional[datetime] = None
    order_details: list[OrderDetail] = None

    class ConfigDict:
        from_attributes = True
