import asyncio
from services.etl import run_recommendation_etl

if __name__ == "__main__":
    asyncio.run(run_recommendation_etl())
