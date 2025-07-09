from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import async_session
from models.stock import Stock
from datetime import date

router = APIRouter()

async def get_db():
    async with async_session() as session:
        yield session

@router.post("/stocks/")
async def add_stock(symbol:str, name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Stock).where(Stock.symbol == symbol)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Stock already in DB")
    
    stock = Stock(symbol=symbol, name= name, added_date= date.today())
    db.add(stock)
    await db.commit()
    return {"message": f"{symbol} added to database"}