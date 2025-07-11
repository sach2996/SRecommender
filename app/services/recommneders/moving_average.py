from .base import BaseRecommender

class MovingAverageRecommender(BaseRecommender):
    def __init__(self, window_size: int = 5):
        self.window_size = window_size

    def recommend(self, prices: list[float]) -> bool:
        if len(prices) < self.window_size:
            print(f"Not enough data: required={self.window_size}, provided={len(prices)}")
            return False
        
        moving_avg = sum(prices[-self.window_size:]) / self.window_size
        current_price = prices[-1]

        print(f"[Recommender] Current price: {current_price}, Moving Avg: {moving_avg}")
        return current_price > moving_avg