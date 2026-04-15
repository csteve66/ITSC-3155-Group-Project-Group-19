from typing import Optional
from pydantic import BaseModel


class SandwichBase(BaseModel):
    sandwich_name: str
    price: float
    calories: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None


class SandwichCreate(SandwichBase):
    pass


class SandwichUpdate(BaseModel):
    sandwich_name: Optional[str] = None
    price: Optional[float] = None
    calories: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None


class Sandwich(SandwichBase):
    id: int

    class ConfigDict:
        from_attributes = True