from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.models.models import RecommendationResponse, StockRequest
from app.services.data import extract_closing_prices, extract_volumes, fetch_stock_data
from app.services.recommenders.moving_average import MovingAverageRecommender
from app.services.recommenders.volume_spike import VolumeSpikeRecommender
from app.services.etl import run_etl_from_csv
from app.services.etl import run_nse_recommendation_etl
from app.services.nse_data import fetch_nsepython_data

router = APIRouter()

def get_recommender():
    return MovingAverageRecommender(window_size=5)

@router.post("/run-recommendations-etl")
async def trigger_etl():
    result = await run_nse_recommendation_etl()
    return {"status": "success", "records_processed": len(result)}

@router.get("/stock/{symbol}")
async def get_stock(symbol: str, interval: str = "5min"):
    data = await fetch_stock_data(symbol, interval)
    if not data:
        raise HTTPException(status_code=500, detail="Failed to fetch stock data")
    return data

@router.get("/nse-stock")
async def get_stock():
    data = await fetch_nsepython_data()
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


@router.post("/upload-csv-etl")
async def upload_csv_etl(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    contents = await file.read()
    result = await run_etl_from_csv(contents, file.filename)
    return {"message": "ETL completed", "processed": len(result)}