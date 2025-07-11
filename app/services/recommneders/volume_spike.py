from .base import BaseRecommender

class VolumeSpikeRecommender(BaseRecommender):
    def __init__(self, window_size: int = 5, multiplier: float = 5.0):
        self.window_size = window_size
        self.multiplier = multiplier

    def recommend(self, volumes: list[int]) -> bool:  # ✅ This must match BaseRecommender
        if len(volumes) <= self.window_size:
            print(f"Not enough volume data: required>{self.window_size}, got={len(volumes)}")
            return False

        avg_volume = sum(volumes[-(self.window_size + 1):-1]) / self.window_size
        today_volume = volumes[-1]

        print(f"[Recommender] Today: {today_volume}, Avg : {avg_volume} (x{self.multiplier})")
        return today_volume > avg_volume * self.multiplier