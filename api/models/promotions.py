from sqlalchemy import Column, Integer, String, DATETIME, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), nullable=False, unique=True)
    discount_percentage = Column(DECIMAL(5, 2), nullable=False)
    expiration_date = Column(DATETIME, nullable=False)

    orders = relationship("Order", back_populates="promotion", foreign_keys="Order.promotion_id")