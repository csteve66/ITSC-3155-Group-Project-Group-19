from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ReviewBase(BaseModel):
    review_text: Optional[str] = None
    score: int = Field(ge=1, le=5)


class ReviewCreate(ReviewBase):
    customer_id: int
    order_id: int


class ReviewUpdate(BaseModel):
    review_text: Optional[str] = None
    score: Optional[int] = Field(default=None, ge=1, le=5)


class Review(ReviewBase):
    id: int
    customer_id: int
    order_id: int

    model_config = ConfigDict(from_attributes=True)
