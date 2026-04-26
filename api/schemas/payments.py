from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict


PaymentType = Literal["card", "cash", "digital_wallet"]
TransactionStatus = Literal["pending", "succeeded", "failed"]


class PaymentBase(BaseModel):
    card_csv: Optional[str] = None
    card_brand: Optional[str] = None
    card_expiration_date: Optional[str] = None
    payment_type: PaymentType


class PaymentCreate(PaymentBase):
    order_id: int


class PaymentUpdate(BaseModel):
    card_csv: Optional[str] = None
    card_brand: Optional[str] = None
    card_expiration_date: Optional[str] = None
    payment_type: Optional[PaymentType] = None


class Payment(PaymentBase):
    id: int
    order_id: int
    transaction_status: TransactionStatus

    model_config = ConfigDict(from_attributes=True)
