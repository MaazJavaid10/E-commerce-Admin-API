from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime




class Category(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Product(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[Category] = None

    class Config:
        from_attributes = True



class SaleBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class Sale(SaleBase):
    id: int
    total_price: float
    sale_date: datetime
    recorded_by: Optional[int] = None
    product: Optional[Product] = None

    class Config:
        from_attributes = True








class PeriodRevenue(BaseModel):
    period: str
    revenue: float

class RevenueComparison(BaseModel):
    period1_revenue: float
    period2_revenue: float
    change_amount: float
    change_percentage: float
    period1_range: str
    period2_range: str
    category_id: Optional[int] = None



class InventoryStatus(BaseModel):
    product_id: int
    product_name: str
    category_id: int
    current_quantity: int
    low_stock_threshold: int
    last_updated: datetime
    low_stock_alert:  Optional[bool] = None


class InventoryUpdateShow(BaseModel):
    product_id: int
    product_name: str
    category_id: int
    current_quantity: int
    low_stock_threshold: int
    last_updated: datetime
    low_stock_alert: bool


class InventoryUpdate(BaseModel):
    new_quantity: int



