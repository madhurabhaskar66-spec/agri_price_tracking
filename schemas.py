from pydantic import BaseModel
from datetime import datetime

class PriceUpdate(BaseModel):
    product_id: int
    new_price: float

    class Config:
        from_attributes = True

class CommodityPriceResponse(BaseModel):
    commodity: str
    market: str
    price: float
    percentage_change: float
    date: datetime

    class Config:
        from_attributes = True