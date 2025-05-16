import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session
from random import randint
from database.database import SessionLocal
from database.models import Category, Product, Inventory, Sale

fake = Faker()


def create_demo_data(db: Session):

    categories = [
        Category(name="Electronics", description="Electronic gadgets and devices"),
        Category(name="Clothing", description="Apparel and fashion items"),
        Category(name="Home & Kitchen", description="Home appliances and kitchenware"),
        Category(name="Books", description="Books and educational materials"),
        Category(name="Sports", description="Sports equipment and gear")
    ]
    db.add_all(categories)
    db.commit()

    products = []
    for i in range(1, 51): 
        category = random.choice(categories)
        price = round(random.uniform(10, 500), 2)
        
        product = Product(
            name=f"{fake.word().capitalize()} {fake.word()}",
            description=fake.sentence(),
            price=price,
            category_id=category.id
        )
        products.append(product)
        db.add(product)
        
        inventory = Inventory(
            product=product,
            quantity=random.randint(0, 200),
            low_stock_threshold=random.choice([5, 10, 15, 20])
        )
        db.add(inventory)
    
    db.commit()

    for i in range(1, 1001):  
        product = random.choice(products)
        quantity = random.randint(1, 5)
        unit_price = product.price * random.uniform(0.9, 1.1) 
        total_price = round(quantity * unit_price, 2)
        
        sale_date = datetime.now() - timedelta(days=random.randint(0, 365))
        
        sale = Sale(
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            sale_date=sale_date,
        )
        db.add(sale)
        
        inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
        if inventory:
            inventory.quantity = max(0, inventory.quantity - quantity)
    
    db.commit()

    products = db.query(Product).all()

    for product in products:
        existing_inventory = db.query(Inventory).filter_by(product_id=product.id).first()
        if not existing_inventory:
            inventory = Inventory(
                product_id=product.id,
                quantity=randint(20, 100),  
                low_stock_threshold=10,
                last_updated=datetime.utcnow()
            )
            db.add(inventory)

    db.commit()

def main():
    db = SessionLocal()
    try:
        print("Starting to populate database with demo data")
        create_demo_data(db)
        print("Successfully populated database with demo data")
    except Exception as e:
        print(f"Error populating database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()