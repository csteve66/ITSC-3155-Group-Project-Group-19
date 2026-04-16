from typing import Optional

from pydantic import BaseModel, ConfigDict


class PaymentBase(BaseModel):
    card_csv: Optional[str] = None
    card_brand: Optional[str] = None
    card_expiration_date: str
    payment_type: str


class PaymentCreate(PaymentBase):
    order_id: int


class PaymentUpdate(BaseModel):
    card_csv: Optional[str] = None
    card_brand: Optional[str] = None
    card_expiration_date: Optional[str] = None
    payment_type: Optional[str] = None


class Payment(PaymentBase):
    id: int
    order_id: int

    model_config = ConfigDict(from_attributes=True)
