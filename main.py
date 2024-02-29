from fastapi import FastAPI
from accounts.auth_routes import auth_router
from orders.order_routes import order_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(order_router)

