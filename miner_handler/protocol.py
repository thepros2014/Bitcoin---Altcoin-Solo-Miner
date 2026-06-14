# miner_handler/protocol.py

import asyncio
import json
from typing import Dict, Optional, Callable
from websockets import connect
import logging

logger = logging.getLogger(__name__)

class StratumProtocol:
    """Stratum mining protocol handler"""
    
    def __init__(self, pool_url: str, wallet: str, worker_name: str):
        self.pool_url = pool_url
        self.wallet = wallet
        self.worker_name = worker_name
        self.ws = None
        self.connected = False
        self_job = None
        self.subscribed = False
    
    async def connect(self) -> bool:
        """Connect to pool via WebSocket"""
        try:
            self.ws = await connect(self.pool_url)
            await self._subscribe()
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    async def _subscribe(self):
        """Subscribe to mining notifications"""
        if not self.ws:
            return
        
        # Mining.subscribe
        subscribe_msg = {
            "id": 1,
            "method": "mining.subscribe",
            "params": [self.worker_name]
        }
        await self.ws.send(json.dumps(subscribe_msg))
