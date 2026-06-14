# miner_handler/factory.py

class MinerFactory:
    """Factory for creating miner handlers"""
    
    @staticmethod
    def create_miner(hardware_type: str, hardware_name: str, pool_config: dict):
        """Create appropriate miner handler"""
        
        if hardware_type == "cpu":
            return CPUMiner(hardware_name, pool_config)
        elif hardware_type == "gpu":
            return GPUMiner(hardware_name, pool_config)
        elif hardware_type == "asic":
            return ASICMiner(hardware_name, pool_config)
        else:
            raise ValueError(f"Unknown hardware type: {hardware_type}")

class CPUMiner(MinerProcess):
    """CPU miner using XMRig"""
    pass

class GPUMiner(MinerProcess):
    """GPU miner using XMRig-NVIDIA or similar"""
    pass

class ASICMiner(MinerProcess):
    """ASIC miner using BFGMiner or similar"""
    pass