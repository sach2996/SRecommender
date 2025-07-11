from pydantic import BaseModel

class StockRequest(BaseModel):
    symbol: str
    interval: str = "DAILY"

class  RecommendationResponse(BaseModel):
    symbol: str
    buy: str
    reason: str