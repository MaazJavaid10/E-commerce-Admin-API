from fastapi import APIRouter, Depends, Query, Path
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from database.database import get_db
from database import models, schemas

router = APIRouter(prefix="/sales", tags=["sales"])

@router.get("/", response_model=List[schemas.Sale])
def get_sales(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    product_ids: Optional[List[int]] = Query(None),
    category_ids: Optional[List[int]] = Query(None),
):
    query = db.query(models.Sale)
    
    if start_date:
        query = query.filter(models.Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(models.Sale.sale_date <= end_date)
    
    if product_ids:
        query = query.filter(models.Sale.product_id.in_(product_ids))
    elif category_ids:
        query = query.join(models.Product).filter(
            models.Product.category_id.in_(category_ids)
        )
    
    return query.order_by(models.Sale.sale_date.desc()).all()

@router.get("/revenue/{period}", response_model=List[schemas.PeriodRevenue])
def get_revenue_by_period(
    period: str = Path(..., description="Group by: day, week, month, or year"),
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):

    if period == "day":
        group_by = func.date(models.Sale.sale_date)
    elif period == "week":
        group_by = func.date_sub(
            func.date(models.Sale.sale_date),
            text("INTERVAL WEEKDAY(sale_date) DAY"),
        )
    elif period == "month":
        group_by = func.date_format(models.Sale.sale_date, "%Y-%m-01")
    elif period == "year":
        group_by = func.date_format(models.Sale.sale_date, "%Y-01-01")
    else:
        valid_periods = ['day', 'week', 'month', 'year']
        if period not in valid_periods:
            return {"error": f"Period must be one of: {', '.join(valid_periods)}"}

    query = db.query(
        group_by.label("period"),
        func.sum(models.Sale.total_price).label("revenue")
    )
    
    if start_date:
        query = query.filter(models.Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(models.Sale.sale_date <= end_date)
    
    results = query.group_by("period").order_by("period").all()
    
    return [
        schemas.PeriodRevenue(period=str(row.period), revenue=float(row.revenue))
        for row in results
    ]

@router.get("/compare", response_model=schemas.RevenueComparison)
def compare_revenue(
    period1_start: datetime,
    period1_end: datetime,
    period2_start: datetime,
    period2_end: datetime,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
):

    query1 = db.query(func.sum(models.Sale.total_price))
    if category_id:
        query1 = query1.join(models.Product).filter(
            models.Product.category_id == category_id
        )
    period1_revenue = (
        query1.filter(
            models.Sale.sale_date >= period1_start,
            models.Sale.sale_date <= period1_end,
        ).scalar() or 0.0
    )
    

    query2 = db.query(func.sum(models.Sale.total_price))
    if category_id:
        query2 = query2.join(models.Product).filter(
            models.Product.category_id == category_id
        )
    period2_revenue = (
        query2.filter(
            models.Sale.sale_date >= period2_start,
            models.Sale.sale_date <= period2_end,
        ).scalar() or 0.0
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

@router.get("/trends/{period}", response_model=List[schemas.SalesTrend])
def get_sales_trends(
    period: str = Path(..., description="Group by: day, week, month, or year"),
    db: Session = Depends(get_db),
    n_periods: int = Query(12, gt=0, le=36),
    category_id: Optional[int] = None,
):
    end_date = datetime.now()
    
    if period == "day":
        start_date = end_date - timedelta(days=n_periods)
        group_by = func.date(models.Sale.sale_date)
    elif period == "week":
        start_date = end_date - timedelta(weeks=n_periods)
        group_by = func.date_sub(
            func.date(models.Sale.sale_date),
            text("INTERVAL WEEKDAY(sale_date) DAY"),
        )
    elif period == "month":
        start_date = end_date - timedelta(days=30 * n_periods)
        group_by = func.date_format(models.Sale.sale_date, "%Y-%m-01")
    elif period == "year":
        start_date = end_date - timedelta(days=365 * n_periods)
        group_by = func.date_format(models.Sale.sale_date, "%Y-01-01")
    else:
        valid_periods = ['day', 'week', 'month', 'year']
        if period not in valid_periods:
            return {"error": f"Period must be one of: {', '.join(valid_periods)}"}
    
    query = db.query(
        group_by.label("period"),
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