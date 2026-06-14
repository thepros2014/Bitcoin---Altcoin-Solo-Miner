# Sortbyprofitability.py

from typing import List, Optional
from models import ProfitData, MinerConfig
from profit_engine.calculator import ProfitCalculator


class ProfitabilitySorter:
    """Sort and filter profitability data"""

    def __init__(self, calculator: ProfitCalculator):
        self.calculator = calculator

    def sort_by_profitability(self, profits: List[ProfitData]) -> List[ProfitData]:
        """Sort by profitability (highest first)"""
        return sorted(profits, key=lambda x: x.profitability, reverse=True)

    async def get_best_coin(self, hardware_type: str) -> Optional[ProfitData]:
        """Get best coin for hardware type"""
        all_profits = await self.calculator.get_all_profits()
        
        # Filter by hardware compatibility
        for profit in all_profits:
            if self._is_compatible(profit, hardware_type):
                return profit
        
        return all_profits[0] if all_profits else None

    def _is_compatible(self, profit: ProfitData, hardware_type: str) -> bool:
        """Check if coin is compatible with hardware"""
        # CPU coins
        cpu_coins = ["monero", "xmr", "qrl", "cryptonight"]
        # GPU coins
        gpu_coins = ["ravencoin", "rvn", "ergo", "erg", "flux", "zel"]
        
        symbol = profit.symbol.lower()
        
        if hardware_type == "cpu":
            return any(c in symbol for c in cpu_coins)
        elif hardware_type == "gpu":
            return any(c in symbol for c in gpu_coins)
        elif hardware_type == "asic":
            return any(c in symbol for c in ["sha256", "bitcoin", "btc"])
        
        return True

    async def calculate_earnings(
        self,
        config: MinerConfig,
        hashrate: float,
        hours: float = 24
    ) -> dict:
        """Calculate estimated earnings"""
        best_coin = await self.get_best_coin(config.hardware_type)
        
        if not best_coin:
            return {"btc": 0, "usd": 0}
        
        # Calculate BTC earnings
        btc_earnings = best_coin.profitability * hashrate * hours
        
        # Convert to USD (assuming $25,000/BTC for simplicity)
        usd_earnings = btc_earnings * 25000
        
        return {
            "btc": btc_earnings,
            "usd": usd_earnings
        }