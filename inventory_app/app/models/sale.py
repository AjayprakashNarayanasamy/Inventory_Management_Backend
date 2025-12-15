from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime

from app.core.database import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_sold = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
