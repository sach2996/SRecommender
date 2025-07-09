import httpx
import os


API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")

async def fetch_stock_data(symbol:str, interval:str):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
    
    