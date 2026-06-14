# models.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime

class HardwareType(str, Enum):
    CPU = "cpu"
    GPU = "gpu"
    ASIC = "asic"

class CoinInfo(BaseModel):
    symbol: str
    name: str
    algorithm: str
    profitability: float  # BTC/day per MH/s or similar
    pool: str

class PoolInfo(BaseModel):
    name: str
    api_url: str
    stratum_url: str
    wallets_needed: bool = True

class MinerConfig(BaseModel):
    wallet_address: str
    hardware_type: HardwareType
    hardware_name: str = "generic"
    electricity_cost: float = 0.10  # $/kWh
    min_profit_threshold: float = 0.05

class Miner(BaseModel):
    miner_id: str
    config: MinerConfig
    current_pool: Optional[str] = None
    status: str = "registered"
    total_earnings: float = 0.0
    earnings_after_fee: float = 0.0
    registered_at: datetime = Field(default_factory=datetime.now)
    last_switch: Optional[datetime] = None

class ProfitData(BaseModel):
    coin: str
    symbol: str
    profitability: float  # BTC/day
    pool: str
    updated_at: datetime

class SwitchRecommendation(BaseModel):
    from_pool: Optional[str]
    to_pool: str
    to_coin: str
    current_profit: float
    new_profit: float
    improvement_percent: float
    recommended: bool