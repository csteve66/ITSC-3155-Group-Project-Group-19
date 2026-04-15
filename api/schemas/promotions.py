from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PromotionBase(BaseModel):
    code: str
    expiration_date: datetime
    order_id: Optional[int] = None


class PromotionCreate(PromotionBase):
    pass


class PromotionUpdate(BaseModel):
    code: Optional[str] = None
    expiration_date: Optional[datetime] = None
    order_id: Optional[int] = None


class Promotion(PromotionBase):
    id: int

    class ConfigDict:
        from_attributes = True