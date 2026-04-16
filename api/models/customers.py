from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..dependencies.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)

    orders = relationship("Order", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")
