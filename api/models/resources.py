from sqlalchemy import Column, Integer, String, DECIMAL
from sqlalchemy.orm import relationship
from ..dependencies.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item = Column(String(100), unique=True, nullable=False)
    amount = Column(DECIMAL(10, 2), index=True, nullable=False, server_default='0.0')
    unit = Column(String(50), nullable=False, server_default='units')

    recipes = relationship("Recipe", back_populates="resource")