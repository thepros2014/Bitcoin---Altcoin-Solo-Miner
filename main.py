# main.py

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, Dict, List
import asyncio
import uuid
from datetime import datetime
import logging

# Import our modules
from config import settings
from models import Miner, MinerConfig, HardwareType, ProfitData
from pools.base import BasePool
from pools.nicehash import NiceHashPool
from pools.miningpoolhub import MiningPoolHubPool
from pools.zpool import ZPool
from profit_engine.calculator import ProfitCalculator
from profit_engine.switcher import ProfitSwitcher
from miner_handler.protocol import StratumProtocol

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LittleMiner API",
    description="Pool aggregator for the little guys - No man left behind",
    version="1.0.0"
)

# In-memory storage
miners: Dict[str, Miner] = {}
profit_calculator = ProfitCalculator()
profit_switcher = ProfitSwitcher(profit_calculator, settings.min_profit_threshold)

# WebSocket connections
websocket_connections: List[WebSocket] = []


@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    logger.info("Starting LittleMiner API")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    logger.info("Shutting down LittleMiner API")
    # Close all pool HTTP clients
    for pool in profit_calculator.pools.values():
        if hasattr(pool, 'close'):
            await pool.close()
    # Cleanup profit calculator
    profit_calculator.cleanup()


@app.get("/")
async def root():
    return {"message": "LittleMiner API is running"}


@app.get("/miners")
async def get_miners():
    return list(miners.values())


@app.post("/miners")
async def register_miner(miner_config: MinerConfig):
    miner_id = str(uuid.uuid4())
    miner = Miner(miner_id=miner_id, config=miner_config)
    miners[miner_id] = miner
    return miner


@app.get("/miners/{miner_id}")
async def get_miner(miner_id: str):
    if miner_id not in miners:
        raise HTTPException(status_code=404, detail="Miner not found")
    return miners[miner_id]


@app.get("/profitability")
async def get_profitability():
    """Get current profitability from all pools (net after convenience fee)."""
    try:
        profits = await profit_calculator.get_all_profits()
        net_profits = profit_calculator.apply_fee_to_profits(profits)
        return {
            "fee_percent": settings.convenience_fee,
            "profits": net_profits
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/profitability/stats")
async def get_profitability_stats():
    """Get profitability statistics"""
    try:
        profits = await profit_calculator.get_all_profits()
        stats = await profit_calculator.get_profitability_stats(profits)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/profitability/best")
async def get_best_profitability():
    """Get the best profitability opportunity (net after convenience fee)."""
    try:
        profits = await profit_calculator.get_all_profits()
        best = profit_calculator.get_best_profitability(profits, apply_fee=True)
        if best:
            return {
                "fee_percent": settings.convenience_fee,
                "best": best
            }
        return {
            "message": "No profitability data available",
            "fee_percent": settings.convenience_fee,
            "best": None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/profitability/switch-recommendation/{miner_id}")
async def get_switch_recommendation(miner_id: str):
    """Get pool switch recommendation for a miner"""
    if miner_id not in miners:
        raise HTTPException(status_code=404, detail="Miner not found")
    
    miner = miners[miner_id]
    current_profit = 0.0  # This would be calculated based on current pool
    
    # For now, we'll just get the latest profits and recommend the best one
    try:
        profits = await profit_calculator.get_all_profits()
        if profits:
            best_profit = profit_calculator.get_best_profitability(profits)
            if best_profit:
                recommendation = await profit_switcher.should_switch(
                    miner, current_profit, best_profit.profitability
                )
                recommendation_dict = recommendation.model_dump()
                recommendation_dict["fee_percent"] = settings.convenience_fee
                return recommendation_dict
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/{miner_id}")
async def websocket_endpoint(websocket: WebSocket, miner_id: str):
    await websocket.accept()
    websocket_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back the data for now
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)