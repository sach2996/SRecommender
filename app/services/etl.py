from app.services.data import fetch_stock_data, extract_closing_prices, extract_volumes
from app.services.recommneders.moving_average import MovingAverageRecommender
from app.services.recommneders.volume_spike import VolumeSpikeRecommender
from app.models.recommendation import Recommendation
from app.db.database import async_session
from app.shared.symbols import SYMBOLS_TO_ANALYZE
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
import asyncio

async def run_recommendation_etl():
    moving_avg = MovingAverageRecommender(window_size=20)
    volume_spike = VolumeSpikeRecommender(window_size=20)

    async with async_session() as session:
        for symbol in SYMBOLS_TO_ANALYZE:
            data = await fetch_stock_data(symbol)

            if not data:
                print(f"Skipping {symbol} due to fetch error.")
                continue

            prices = extract_closing_prices(data)
            volumes = extract_volumes(data)

            if prices:
                decision = moving_avg.recommend(prices)
                await save_recommendation(session, symbol, "moving_average", decision)

            if volumes:
                decision = volume_spike.recommend(volumes)
                await save_recommendation(session, symbol, "volume_spike", decision)
        
        await session.commit()

async def save_recommendation(
        session: AsyncSession,
        symbol: str,
        strategy: str,
        decision: bool
):
    today = str(date.today())
    rec = Recommendation(
        symbol = symbol,
        strategy = strategy,
        buy = decision,
        date = today
    )
    session.add(rec)