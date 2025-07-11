from fastapi import APIRouter, Depends, HTTPException
from app.models.models import RecommendationResponse, StockRequest
from app.services.data import extract_closing_prices, extract_volumes, fetch_stock_data
from app.services.recommneders.moving_average import MovingAverageRecommender
from app.services.recommneders.volume_spike import VolumeSpikeRecommender

router = APIRouter()

def get_recommender():
    return MovingAverageRecommender(window_size=5)

@router.get("/stock/{symbol}")
async def get_stock(symbol: str, interval: str = "5min"):
    data = await fetch_stock_data(symbol, interval)
    if not data:
        raise HTTPException(status_code=500, detail="Failed to fetch stock data")
    return data

@router.post("recommend", response_model=RecommendationResponse)
async def recommend_Stock(
    payload: StockRequest,
    recommender = Depends(get_recommender)
):
    data = await fetch_stock_data(payload.symbol, payload.interval)
    if not data:
        raise HTTPException(status_code=502, detail="Failed to fetch stock data")
    
    prices = extract_closing_prices(data)
    if not prices:
        raise HTTPException(status_code=400, detail="Could not extract prices")
    
    decision = recommender.recommend(prices)
    reason = f"Current price is {'above' if decision else 'below'} the moving average"

    return RecommendationResponse(symbol=payload.symbol, buy=decision, reason=reason)


@router.post("/volume-spike", response_model=RecommendationResponse)
async def recommend_by_volume(
    payload: StockRequest,
    recommender = Depends(lambda: VolumeSpikeRecommender(window_size=20))
):
    data = await fetch_stock_data(payload.symbol, payload.interval)
    if not data:
        raise HTTPException(status_code=502, detail="Failde to fetch stock data")
    
    volumes = extract_volumes(data)
    if not volumes:
        raise HTTPException(status_code=400, detail="Could not extract volume data")
    
    decision = recommender.recommend(volumes)
    reason = f"Today's volume is {'high' if decision else 'normal'} compared to 20-day avg"
    
    return RecommendationResponse(symbol=payload.symbol, buy=decision, reason=reason)