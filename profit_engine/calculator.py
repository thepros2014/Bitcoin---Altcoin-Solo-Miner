# profit_engine/calculator.py

from typing import List, Dict, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
from models import ProfitData, MinerConfig
from pools.nicehash import NiceHashPool
from pools.miningpoolhub import MiningPoolHubPool
from pools.zpool import ZPool
import statistics
import logging
from config import settings

logger = logging.getLogger(__name__)


class ProfitCalculator:
    """Calculate profitability across pools"""

    def __init__(self):
        self.pools = {
            "nicehash": NiceHashPool(),
            "mph": MiningPoolHubPool(),
            "zpool": ZPool(),
        }
        # Thread pool for CPU-intensive calculations
        self._thread_pool = ThreadPoolExecutor(max_workers=4)

    async def get_all_profits(self) -> List[ProfitData]:
        """Get profitability from all pools"""
        all_profits = []

        # Create tasks for concurrent execution
        tasks = []
        for pool_name, pool in self.pools.items():
            task = asyncio.create_task(self._get_pool_profits(pool_name, pool))
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, (pool_name, _) in enumerate(self.pools.items()):
            result = results[i]
            if isinstance(result, Exception):
                logger.exception("Error getting profits from %s: %s", pool_name, result)
            else:
                all_profits.extend(result)

        return all_profits

    async def _get_pool_profits(self, pool_name: str, pool) -> List[ProfitData]:
        """Get profits from a single pool with error handling"""
        try:
            return await pool.get_profitability()
        except Exception as e:
            logger.exception("Error getting profits from %s: %s", pool_name, e)
            return []

    async def get_profitability_stats(self, profits: List[ProfitData]) -> Dict[str, float]:
        """Calculate statistics from profitability data (CPU-intensive)"""
        if not profits:
            return {}

        # Use thread pool for CPU-intensive calculations
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._thread_pool,
            self._calculate_profitability_stats,
            profits
        )

    def _calculate_profitability_stats(self, profits: List[ProfitData]) -> Dict[str, float]:
        """Calculate profitability statistics (runs in thread pool)"""
        if not profits:
            return {}

        # Extract profitability values
        profit_values = [p.profitability for p in profits]

        # Calculate various statistics
        stats = {
            "count": len(profit_values),
            "mean": statistics.mean(profit_values) if profit_values else 0,
            "median": statistics.median(profit_values) if profit_values else 0,
            "stdev": statistics.stdev(profit_values) if len(profit_values) > 1 else 0,
            "min": min(profit_values) if profit_values else 0,
            "max": max(profit_values) if profit_values else 0,
        }

        # Group by pool and calculate pool-specific stats
        pool_profits = {}
        for profit in profits:
            if profit.pool not in pool_profits:
                pool_profits[profit.pool] = []
            pool_profits[profit.pool].append(profit.profitability)

        for pool_name, values in pool_profits.items():
            stats[f"{pool_name}_mean"] = statistics.mean(values) if values else 0
            stats[f"{pool_name}_max"] = max(values) if values else 0

        return stats

    def apply_fee_to_profits(self, profits: List[ProfitData], fee_percent: Optional[float] = None) -> List[ProfitData]:
        """Return profitability data after applying convenience fee."""
        if not profits:
            return []
        fee = settings.convenience_fee if fee_percent is None else fee_percent
        net_multiplier = max(0.0, 1.0 - fee)
        return [
            p.model_copy(update={"profitability": p.profitability * net_multiplier})
            for p in profits
        ]

    def get_best_profitability(self, profits: List[ProfitData], apply_fee: bool = True) -> Optional[ProfitData]:
        """Get the highest profitability entry; applies configured fee by default."""
        if not profits:
            return None
        candidate_profits = self.apply_fee_to_profits(profits) if apply_fee else profits
        return max(candidate_profits, key=lambda p: p.profitability)

    def filter_profitable_coins(
        self,
        profits: List[ProfitData],
        min_profitability: float,
        apply_fee: bool = True
    ) -> List[ProfitData]:
        """Filter coins by minimum profitability threshold; applies configured fee by default."""
        if not profits:
            return []
        candidate_profits = self.apply_fee_to_profits(profits) if apply_fee else profits
        return [p for p in candidate_profits if p.profitability >= min_profitability]

    def cleanup(self):
        """Cleanup resources"""
        self._thread_pool.shutdown(wait=True)