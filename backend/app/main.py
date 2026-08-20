from fastapi import FastAPI

from app.auth import router as auth_router
from app.listings import router as listings_router
from app.orders import router as orders_router
from app.payments import router as payments_router

app = FastAPI(title="Quadgig API")
app.include_router(auth_router)
app.include_router(listings_router)
app.include_router(orders_router)
app.include_router(payments_router)


@app.get("/health")
def health():
    return {"status": "ok"}
