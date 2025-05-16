# E-Commerce Admin API

A FastAPI-based backend project for managing inventory and tracking sales analytics. It provides powerful endpoints to fetch revenue trends, sales comparisons, and inventory status for real-time business insights.


## Features

- **Inventory Management**: Track product quantities, set threshold alerts, and manage stock
- **Sales Analytics**: Visualize revenue trends and generate performance reports
- **Database Migrations**: Easy database versioning with Alembic

## Technology Stack

- [FastAPI]: Modern, high-performance web framework
- [SQLAlchemy]: SQL toolkit and ORM
- [Alembic]: Database migration tool
- [PyMySQL]: MySQL connector for Python
- [Pydantic]: Data validation and settings management

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/MaazJavaid10/E-commerce-Admin-API.git
cd E-commerce-Admin-API
```

### 2. Create and Activate Virtual Environment
**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Database Setup

### 1. Configure Database Connection
Edit the `alembic.ini` file to set your database connection:
```
sqlalchemy.url = mysql+pymysql://username:password@localhost/ecommerce_db
```

### 2. Generate and Run Migrations
First, create the migration file:
```bash
alembic revision --autogenerate -m "Initial tables"
```

Then apply the migrations to create all database tables:
```bash
alembic upgrade head
```

### 3. Populate Initial Data (Optional)
```bash
python script/populate_db.py
```

## Database Schema Documentation

### Tables

#### Categories
- `id`: Primary key
- `name`: Category name (unique)
- `description`: Category description
- Relationships: One-to-many with Products

#### Products
- `id`: Primary key
- `name`: Product name
- `description`: Product description
- `price`: Product price
- `category_id`: Foreign key to Categories
- Relationships: 
  - Many-to-one with Categories
  - One-to-one with Inventory
  - One-to-many with Sales

#### Inventory
- `id`: Primary key
- `product_id`: Foreign key to Products (unique)
- `quantity`: Current stock quantity
- `low_stock_threshold`: Alert threshold
- Relationships: One-to-one with Products

#### Sales
- `id`: Primary key
- `product_id`: Foreign key to Products
- `quantity`: Quantity sold
- `unit_price`: Price per unit at time of sale
- `total_price`: Total sale amount
- `sale_date`: Date of sale
- Relationships: Many-to-one with Products


## Running the Application

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

## API Endpoints

### Sales
- `GET /sales/` - Get sales with filters
- `GET /sales/revenue/{period}` - Revenue by period (day/week/month/year)
- `GET /sales/compare` - Compare revenue between periods
- `GET /sales/trends/{period}` - Sales trends

### Inventory
- `GET /inventory/` - Current inventory status
- `PUT /inventory/{product_id}` - Update inventory


---
