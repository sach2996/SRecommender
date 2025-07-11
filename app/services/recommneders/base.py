from abc import ABC, abstractmethod
from typing import Protocol

class BaseRecommender(ABC):
    @abstractmethod
    def recommend(self, prices: list[float]) -> bool:
        """Return True if BUY signal, else False."""
        pass