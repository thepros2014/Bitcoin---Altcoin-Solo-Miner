# Mining.authorize
        authorize_msg = {
            "id": 2,
            "method": "mining.authorize",
            "params": [self.wallet, ""]
        }
        await self.ws.send(json.dumps(authorize_msg))
    
    async def get_job(self) -> Optional[Dict]:
        """Get mining job from pool"""
        if not self.ws:
            return None
        
        try:
            msg = await asyncio.wait_for(self.ws.recv(), timeout=5)
            data = json.loads(msg)
            
            if data.get("method") == "mining.notify":
                return data.get("params")
        except:
            pass
        return None
    
    async def submit_share(self, job_id: str, nonce: int, result: str) -> bool:
        """Submit solved share"""
        if not self.ws:
            return False
        
        submit_msg = {
            "id": 3,
            "method": "mining.submit",
            "params": [self.worker_name, job_id, nonce, result]
        }
        await self.ws.send(json.dumps(submit_msg))
        return True
    
    async def disconnect(self):
        """Disconnect from pool"""
        if self.ws:
            await self.ws.close()
            self.connected = False
