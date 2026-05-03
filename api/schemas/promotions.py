from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class PromotionBase(BaseModel):
    code: str
    discount_percentage: float = Field(..., ge=0, le=100, description="Discount as a percentage (0-100)")
    expiration_date: datetime


class PromotionCreate(PromotionBase):
    pass


class PromotionUpdate(BaseModel):
    code: Optional[str] = None
    discount_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    expiration_date: Optional[datetime] = None


class Promotion(PromotionBase):
    id: int

    class ConfigDict:
        from_attributes = True


class PromotionValidateResponse(BaseModel):
    valid: bool
    discount_percentage: Optional[float] = None
    message: str