# profit_engine/switcher.py

from typing import Optional
from datetime import datetime
from models import SwitchRecommendation, Miner, ProfitData

class ProfitSwitcher:
    """Auto-switch pools for maximum profit"""
    
    def __init__(self, calculator: ProfitCalculator, min_threshold: float = 0.05):
        self.calculator = calculator
        self.min_threshold = min_threshold
    
    async def should_switch(
        self,
        miner: Miner,
        current_profit: float,
        new_profit: float
    ) -> Optional[SwitchRecommendation]:
        """Determine if pool switch is recommended"""
        
        if current_profit == 0:
            return None
        
        improvement = (new_profit - current_profit) / current_profit
        
        if improvement >= self.min_threshold:
            return SwitchRecommendation(
                from_pool=miner.current_pool,
                to_pool="auto",  # Would determine best pool
                to_coin="auto",
                current_profit=current_profit,
                new_profit=new_profit,
                improvement_percent=improvement * 100,
                recommended=True,
            )
        
        return SwitchRecommendation(
            from_pool=miner.current_pool,
            to_pool=miner.current_pool,
            to_coin="current",
            current_profit=current_profit,
            new_profit=new_profit,
            improvement_percent=improvement * 100,
            recommended=False,
        )
