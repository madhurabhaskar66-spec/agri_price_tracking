from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ProductPrice(Base):
    __tablename__ = "product_prices"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    price_per_kg = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    old_price = Column(Float)
    new_price = Column(Float)
    percentage_change = Column(Float)
    alert_type = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CommodityPrice(Base):
    __tablename__ = "commodity_prices"

    id = Column(Integer, primary_key=True, index=True)
    commodity = Column(String)
    market = Column(String)
    price = Column(Float)
    percentage_change = Column(Float)
    date = Column(DateTime)