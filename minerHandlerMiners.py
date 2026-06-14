# miner_handler/miners.py

import subprocess
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MinerProcess:
    """Wrapper for external mining software"""
    
    def __init__(self, miner_binary: str, config: dict):
        self.miner_binary = miner_binary
        self.config = config
        self.process: Optional[subprocess.Popen] = None
    
    def build_args(self) -> list:
        """Build command line arguments"""
        args = [self.miner_binary]
        
        # Add pool URL
        args.extend(["-o", self.config.get("pool_url", "")])
        
        # Add wallet
        args.extend(["-u", self.config.get("wallet", "")])
        
        # Add worker
        if self.config.get("worker"):
            args.extend(["--worker", self.config.get("worker")])
        
        # Algorithm
        if self.config.get("algorithm"):
            args.extend(["-a", self.config.get("algorithm")])
        
        # Add any extra params
        for k, v in self.config.get("extra", {}).items():
            args.extend([f"--{k}", str(v)])
        
        return args
    
    def start(self) -> bool:
        """Start the miner process"""
        try:
            args = self.build_args()
            self.process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logger.info(f"Started miner: {' '.join(args)}")
            return True
        except Exception as e:
            logger.error(f"Failed to start miner: {e}")
            return False
    
    def stop(self):
        """Stop the miner process"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
    
    def is_running(self) -> bool:
        """Check if miner is running"""
        return self.process and self.process.poll() is None
