from fastapi import FastAPI
from app.api import endpoints
from app.db.database import engine
from app.models.stock import Base

app = FastAPI(title="StockRecommender")

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await create_tables()

app.include_router(endpoints.router)