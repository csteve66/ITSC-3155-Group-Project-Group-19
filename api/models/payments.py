from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..dependencies.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    card_csv = Column(String(3), nullable=True)
    card_brand = Column(String(50), nullable=True)
    card_expiration_date = Column(String(5), nullable=True)
    payment_type = Column(String(50), nullable=False)
    transaction_status = Column(String(20), nullable=False, server_default="pending")

    order = relationship("Order", back_populates="payments")
