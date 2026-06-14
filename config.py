# config.py

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Pool Settings
    switch_interval: int = 60  # seconds
    min_profit_threshold: float = 0.05  # 5% before switching
    
    # Mining Settings
    default_pool: str = "nicehash"
    backup_pool: str = "zpool"
    
    # Fee Settings (2%)
    convenience_fee: float = 0.02
    
    # Supported Pools
    supported_pools: List[str] = ["nicehash", "mph", "zpool"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
