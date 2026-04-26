from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    customer_name = Column(String(100))
    customer_phone = Column(String(50), nullable=True)
    customer_address = Column(String(500), nullable=True)
    order_date = Column(DATETIME, nullable=False, server_default=str(datetime.now()))
    description = Column(String(300))

    customer = relationship("Customer", back_populates="orders")
    promotions = relationship("Promotion", back_populates="order")
    order_details = relationship("OrderDetail", back_populates="order")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    review = relationship("Review", back_populates="order", uselist=False)