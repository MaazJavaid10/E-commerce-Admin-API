from fastapi import FastAPI
from routers import sales, inventory

app = FastAPI()


app.include_router(sales.router)
app.include_router(inventory.router)
