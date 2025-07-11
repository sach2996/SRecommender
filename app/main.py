from fastapi import FastAPI
from app.api import endpoints
from app.db.database import engine
from app.models.recommendation import Base
from fastapi.middleware.cors import CORSMiddleware
origins = [
    "http://localhost",
    "http://localhost:4200",
    # Add more origins as needed
]

app = FastAPI(title="StockRecommender")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await create_tables()

app.include_router(endpoints.router)