from fastapi import APIRouter
from app.services.alphavantage import fetch_stock_data

router = APIRouter()

@router.get("/stock/{symbol}")
async def get_stock(symbol: str, interval: str = "5min"):
    return await fetch_stock_data(symbol, interval)