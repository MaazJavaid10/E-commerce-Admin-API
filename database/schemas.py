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


class InventoryBase(BaseModel):
    quantity: int = Field(..., ge=0)
    low_stock_threshold: int = Field(10, ge=0)


class Inventory(InventoryBase):
    id: int
    product_id: int
    last_updated: datetime
    product: Optional[Product] = None

    class Config:
        from_attributes = True

class InventoryAdjustment(BaseModel):
    change_amount: int
    change_type: str   
    notes: Optional[str] = None



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


class RevenueAnalysis(BaseModel):
    period: str
    total_revenue: float
    total_sales: int
    top_products: List[dict]
    comparison_to_previous: Optional[float] = None


class LowStockAlert(BaseModel):
    product_id: int
    product_name: str
    current_quantity: int
    low_stock_threshold: int
    last_updated: datetime





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

class SalesTrend(BaseModel):
    period: str
    sales_count: int
    total_quantity: int
    total_revenue: float

class InventoryStatus(BaseModel):
    product_id: int
    product_name: str
    category_id: int
    current_quantity: int
    low_stock_threshold: int
    last_updated: datetime
    low_stock_alert:  Optional[bool] = None



class InventoryUpdate(BaseModel):
    new_quantity: int



