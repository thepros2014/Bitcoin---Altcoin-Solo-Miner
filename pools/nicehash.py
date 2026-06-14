# pools/nicehash.py

from .base import BasePool
from models import ProfitData, PoolInfo
from datetime import datetime


class NiceHashPool(BasePool):
    """NiceHash API integration"""

    def __init__(self):
        super().__init__("nicehash")
        self.pool_info = PoolInfo(
            name="nicehash",
            api_url="https://api.nicehash.com/main/api/v2/mining/public/profit/latest",
            stratum_url="stratum+tcp://nicehash.com:3333",
        )

    async def get_profitability(self) -> List[ProfitData]:
        """Get profitability from NiceHash"""
        data = await self.fetch_json(self.pool_info.api_url)
        if not data:
            return []

        profits = []
        for algo in data.get("miningAlgorithms", []):
            profits.append(ProfitData(
                coin=algo.get("algorithm", {}).get("displayName", "Unknown"),
                symbol=algo.get("algorithm", {}).get("name", ""),
                profitability=float(algo.get("price", 0)),
                pool="nicehash",
                updated_at=datetime.now(),
            ))
        return profits

    async def submit_hashrate(self, worker_id: str, hashrate: float) -> bool:
        """Submit hashrate to NiceHash (not implemented for this example)"""
        # In a real implementation, this would submit hashrate to the pool
        # For now, we'll just return True to indicate success
        return True

    def get_balance(self, wallet: str) -> float:
        """Get pending balance for wallet from NiceHash (not implemented for this example)"""
        # In a real implementation, this would query the NiceHash API for balance
        # For now, we'll return 0.0
        return 0.0