# database/crud_inventory.py
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from database import models, schemas
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.sql import func, text




class InventoryCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get_inventory_status(
        self,
        low_stock_only: bool = False,
        category_id: Optional[int] = None,
    ) -> List[schemas.InventoryStatus]:
        query = self.db.query(models.Inventory, models.Product).join(models.Product)

        if low_stock_only:
            query = query.filter(
                models.Inventory.quantity <= models.Inventory.low_stock_threshold
            )

        if category_id:
            query = query.filter(models.Product.category_id == category_id)

        results = query.all()

        return [
            schemas.InventoryStatus(
                product_id=inventory.product_id,
                product_name=product.name,
                category_id=product.category_id,
                current_quantity=inventory.quantity,
                low_stock_threshold=inventory.low_stock_threshold,
                last_updated=inventory.last_updated,
            )
            for inventory, product in results
        ]

    def update_inventory(
        self,
        product_id: int,
        new_quantity: int,
    ) -> models.Inventory:
        inventory, product = self.db.query(models.Inventory, models.Product).join(
            models.Product
        ).filter(models.Inventory.product_id == product_id).first() or (None, None)

        if not inventory or not product:
            raise ValueError("Product not found in inventory")

        if new_quantity < 0:
            raise ValueError("Inventory quantity cannot be negative")

        inventory.quantity = new_quantity
        inventory.last_updated = datetime.now()
        self.db.commit()
        self.db.refresh(inventory)

        return schemas.InventoryStatus(
            product_id=inventory.product_id,
            product_name=product.name,
            category_id=product.category_id,
            current_quantity=inventory.quantity,
            low_stock_threshold=inventory.low_stock_threshold,
            last_updated=inventory.last_updated,
        )


class SalesCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get_sales(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        product_ids: Optional[List[int]] = None,
        category_ids: Optional[List[int]] = None,
    ) -> List[models.Sale]:
        query = self.db.query(models.Sale)

        # Apply date filters
        if start_date:
            query = query.filter(models.Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(models.Sale.sale_date <= end_date)

        # Apply product/category filters
        if product_ids:
            query = query.filter(models.Sale.product_id.in_(product_ids))
        elif category_ids:
            query = query.join(models.Product).filter(
                models.Product.category_id.in_(category_ids)
            )

        return query.order_by(models.Sale.sale_date.desc())

    def get_revenue_by_period(
        self,
        period: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[schemas.PeriodRevenue]:

        if period == "day":
            trunc_expr = func.date(models.Sale.sale_date)
        elif period == "week":
            trunc_expr = func.date_sub(
                func.date(models.Sale.sale_date),
                text("INTERVAL WEEKDAY(sale_date) DAY"),
            )
        elif period == "month":
            trunc_expr = func.date_format(models.Sale.sale_date, "%Y-%m-01")
        elif period == "year":
            trunc_expr = func.date_format(models.Sale.sale_date, "%Y-01-01")
        else:
            raise ValueError(
                "Invalid period. Must be 'day', 'week', 'month', or 'year'"
            )

        query = self.db.query(
            trunc_expr.label("period"),
            func.sum(models.Sale.total_price).label("revenue"),
        )

        if start_date:
            query = query.filter(models.Sale.sale_date >= start_date)
        if end_date:
            query = query.filter(models.Sale.sale_date <= end_date)

        query = query.group_by("period").order_by("period")
        results = query.all()

        return [
            schemas.PeriodRevenue(period=str(row.period), revenue=float(row.revenue))
            for row in results
        ]

    def get_revenue_comparison(
        self,
        period1_start: datetime,
        period1_end: datetime,
        period2_start: datetime,
        period2_end: datetime,
        category_id: Optional[int] = None,
    ) -> schemas.RevenueComparison:
        query1 = self.db.query(func.sum(models.Sale.total_price))
        if category_id:
            query1 = query1.join(models.Product).filter(
                models.Product.category_id == category_id
            )
        period1_revenue = (
            query1.filter(
                and_(
                    models.Sale.sale_date >= period1_start,
                    models.Sale.sale_date <= period1_end,
                )
            ).scalar()
            or 0.0
        )

        query2 = self.db.query(func.sum(models.Sale.total_price))
        if category_id:
            query2 = query2.join(models.Product).filter(
                models.Product.category_id == category_id
            )
        period2_revenue = (
            query2.filter(
                and_(
                    models.Sale.sale_date >= period2_start,
                    models.Sale.sale_date <= period2_end,
                )
            ).scalar()
            or 0.0
        )

        change_amount = period2_revenue - period1_revenue
        change_percentage = (
            (change_amount / period1_revenue * 100) if period1_revenue else 0.0
        )

        return schemas.RevenueComparison(
            period1_revenue=period1_revenue,
            period2_revenue=period2_revenue,
            change_amount=change_amount,
            change_percentage=change_percentage,
            period1_range=f"{period1_start.date()} to {period1_end.date()}",
            period2_range=f"{period2_start.date()} to {period2_end.date()}",
            category_id=category_id,
        )

    def get_sales_trends(
        self,
        period: str, 
        n_periods: int = 12,
        category_id: Optional[int] = None,
    ) -> List[schemas.SalesTrend]:
        end_date = datetime.now()

        if period == "day":
            start_date = end_date - timedelta(days=n_periods)
            trunc_expr = func.date(models.Sale.sale_date)
        elif period == "week":
            start_date = end_date - timedelta(weeks=n_periods)
            # Truncate to start of week (Sunday)
            trunc_expr = func.date_sub(
                func.date(models.Sale.sale_date),
                text("INTERVAL WEEKDAY(sale_date) DAY"),
            )
        if period == "month":
            start_date = end_date - timedelta(days=30 * n_periods)
            trunc_expr = func.date(models.Sale.sale_date)
        else:  # 'year'
            start_date = end_date - timedelta(days=365 * n_periods)
            trunc_expr = func.date_format(models.Sale.sale_date, "%Y-01-01")

        query = self.db.query(
            trunc_expr.label("period"),
            func.count(models.Sale.id).label("sales_count"),
            func.sum(models.Sale.quantity).label("total_quantity"),
            func.sum(models.Sale.total_price).label("total_revenue"),
        ).filter(models.Sale.sale_date.between(start_date, end_date))

        if category_id:
            query = query.join(models.Product).filter(
                models.Product.category_id == category_id
            )

        results = query.group_by("period").order_by("period").all()

        return [
            schemas.SalesTrend(
                period=str(row.period),
                sales_count=row.sales_count,
                total_quantity=row.total_quantity,
                total_revenue=row.total_revenue,
            )
            for row in results
        ]
