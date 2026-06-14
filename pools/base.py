# pools/base.py

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from models import ProfitData, PoolInfo
from datetime import datetime
import httpx
import time
import hashlib
import json


class BasePool(ABC):
    """Base class for pool integrations"""

    def __init__(self, name: str):
        self.name = name
        self.pool_info: PoolInfo
        # Connection pool for HTTP requests
        self._http_client: Optional[httpx.AsyncClient] = None
        # Cache for API responses
        self._cache: Dict[str, Dict] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_ttl = 30  # Cache TTL in seconds

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with connection pooling"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
                timeout=httpx.Timeout(10.0)
            )
        return self._http_client

    async def close(self):
        """Close HTTP client"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        return hashlib.md5(url.encode()).hexdigest()

    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cache entry is still valid"""
        return time.time() - timestamp < self._cache_ttl

    def _get_from_cache(self, url: str) -> Optional[Dict]:
        """Get data from cache if valid"""
        cache_key = self._get_cache_key(url)
        if cache_key in self._cache and self._is_cache_valid(self._cache_timestamps[cache_key]):
            return self._cache[cache_key]
        return None

    def _save_to_cache(self, url: str, data: Dict):
        """Save data to cache"""
        cache_key = self._get_cache_key(url)
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = time.time()

    @abstractmethod
    async def get_profitability(self) -> List[ProfitData]:
        """Fetch profitability data from pool"""
        pass

    @abstractmethod
    async def submit_hashrate(self, worker_id: str, hashrate: float) -> bool:
        """Submit hashrate to pool"""
        pass

    @abstractmethod
    def get_balance(self, wallet: str) -> float:
        """Get pending balance for wallet"""
        pass

    async def fetch_json(self, url: str) -> Optional[Dict]:
        """Helper for HTTP requests with caching and connection pooling"""
        # Check cache first
        cached_data = self._get_from_cache(url)
        if cached_data is not None:
            return cached_data

        # Fetch fresh data
        try:
            client = await self._get_http_client()
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                # Save to cache
                self._save_to_cache(url, data)
                return data
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None