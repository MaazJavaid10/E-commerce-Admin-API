from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from database.database import get_db
from database import models, schemas

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("/", response_model=List[schemas.InventoryStatus])
def get_inventory_status(
    db: Session = Depends(get_db),
    low_stock_only: Optional[bool] = None,
    category_id: Optional[int] = None,
):
    query = db.query(models.Inventory, models.Product).join(models.Product)
    
    if low_stock_only is True:
        query = query.filter(models.Inventory.quantity <= models.Inventory.low_stock_threshold)
    elif low_stock_only is False:
        query = query.filter(models.Inventory.quantity > models.Inventory.low_stock_threshold)

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
            low_stock_alert=inventory.quantity <= inventory.low_stock_threshold,
        )
        for inventory, product in results
    ]

@router.put("/{product_id}", response_model=schemas.InventoryStatus)
def update_inventory_item(
    product_id: int,
    inventory_update: schemas.InventoryUpdate,
    db: Session = Depends(get_db),
):

    result = db.query(models.Inventory, models.Product).join(
        models.Product
    ).filter(models.Inventory.product_id == product_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Product not found in inventory")
    
    inventory, product = result
    
    if inventory_update.new_quantity < 0:
        raise HTTPException(status_code=400, detail="Inventory quantity cannot be negative")
    
    inventory.quantity = inventory_update.new_quantity
    inventory.last_updated = datetime.now()
    
    db.commit()
    db.refresh(inventory)
    
    return schemas.InventoryUpdateShow(
        product_id=inventory.product_id,
        product_name=product.name,
        category_id=product.category_id,
        current_quantity=inventory.quantity,
        low_stock_threshold=inventory.low_stock_threshold,
        last_updated=inventory.last_updated,
        low_stock_alert=inventory.quantity <= inventory.low_stock_threshold,
    )
