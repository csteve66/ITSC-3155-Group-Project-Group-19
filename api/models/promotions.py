from sqlalchemy import Column, Integer, String, DATETIME, ForeignKey
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), nullable=False, unique=True)
    expiration_date = Column(DATETIME, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)

    order = relationship("Order", back_populates="promotions")