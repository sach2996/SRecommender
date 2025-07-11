import httpx
import os
from typing import Optional
import csv
import requests
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
API_LIMIT_MESSAGE = "standard API rate limit is 25 requests per day"
DATA_PATH = "app/shared/data/historical_stock_data.csv"


if not API_KEY:
    raise ValueError("API Key is not set in environment variables")
async def fetch_stock_data(symbol:str, interval:str = "DAILY") -> Optional[dict]:
    # function = "TIME_SERIES_DAILY" if interval.upper() == "DAILY" else "TIME_SERIES_INTRADAY"
    # print(f"function {function}")
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'
    return load_stock_data_from_csv(symbol)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            if 'Information' in data and API_LIMIT_MESSAGE in data['Information']:
                print(f"[WARNING] API limit reached, loading data from CSV for {symbol}")
                return load_stock_data_from_csv(symbol)
        
            if "Time Series" not in str(data):
                raise ValueError(f"Unexpected response: {data}")
            return data
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as e:
        print(f"[ERROR] Failed to fetch stock data: {e}")
        return None
    

def extract_closing_prices(data: dict) -> list[float]:
    try:
        # Find the dict with key containing "Time Series"
        time_series = next((v for k, v in data.items() if "Time Series" in k), None)
        if not time_series:
            return []

        # Sort by date (keys), then extract closing prices as float
        prices = [float(day_data["4. close"]) for _, day_data in sorted(time_series.items())]
        return prices
    except Exception as e:
        print(f"[ERROR] Parsing failed: {e}")
        return []

def extract_volumes(data: dict) -> list[int]:
    try:
        time_series = next((v for k, v in data.items() if "Time Series" in k), None)
        if not time_series:
            return []

        # Sort by date and extract volumes as int
        volumes = [int(day_data["5. volume"]) for _, day_data in sorted(time_series.items())]
        return volumes
    except Exception as e:
        print(f"[ERROR] Parsing volumes failed: {e}")
        return []

def load_stock_data_from_csv(symbol: str) -> dict:
    stock_data = {}
    print(symbol)
    if not os.path.exists(DATA_PATH):
        print(f"[ERROR] CSV file not found at {DATA_PATH}")
        return None

    try:
        with open(DATA_PATH, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['symbol'].upper() == symbol.upper():
                    stock_data[row['date']] = {
                        '1. open': row['open'],
                        '2. high': row['high'],
                        '3. low': row['low'],
                        '4. close': row['close'],
                        '5. volume': row['volume'],
                    }
        if not stock_data:
            print(f"[WARN] No data found in CSV for {symbol}")
        return stock_data
    except Exception as e:
        print(f"[ERROR] Failed to read CSV: {e}")
        return None