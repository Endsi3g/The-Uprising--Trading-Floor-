import httpx
import asyncio
import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MasterTestSuite")

# Base URLs
SERVICES = {
    "BrokerHub": "http://broker-hub:8001/health",
    "NewsHub": "http://news-hub:8002/health",
    "AIService": "http://ai-service:8003/health",
    "RiskEngine": "http://risk-engine:8004/health",
    "AlertHub": "http://alert-hub:8005/health"
}

class MasterTestSuite:
    async def check_health(self):
        print("\n--- Service Health Check ---")
        async with httpx.AsyncClient(timeout=5.0) as client:
            for name, url in SERVICES.items():
                try:
                    resp = await client.get(url)
                    status = "✅ OK" if resp.status_code == 200 else "❌ FAIL"
                    print(f"{name:12}: {status} ({resp.status_code})")
                except Exception as e:
                    print(f"{name:12}: ❌ ERROR ({str(e)})")

    async def verify_e2e_flow(self):
        print("\n--- E2E Flow Verification (Market -> AI -> Risk -> Alert) ---")
        
        # 1. Simulate AI Analysis
        print("1. Testing AI Analysis...")
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                ai_resp = await client.post("http://ai-service:8003/ai/analyze", json={
                    "context": "Market is trending up, volume is high.",
                    "instruction": "Provide a quick summary."
                })
                if ai_resp.status_code == 200:
                    print("   ✅ AI analysis triggered successfully.")
                else:
                    print(f"   ❌ AI analysis failed: {ai_resp.text}")
            except Exception as e:
                print(f"   ❌ AI analysis error: {e}")

        # 2. Simulate Risk Check
        print("2. Testing Risk Validation...")
        try:
            risk_resp = await client.post("http://risk-engine:8004/risk/check", json={
                "symbol": "BTC/USDT",
                "side": "buy",
                "amount": 100.0,
                "current_pnl": -50.0  # Trigger stop-loss simulation
            })
            if risk_resp.status_code == 200:
                data = risk_resp.json()
                print(f"   ✅ Risk check successful. Allowed: {data['allowed']}, MSG: {data['message']}")
            else:
                print(f"   ❌ Risk check failed: {risk_resp.text}")
        except Exception as e:
            print(f"   ❌ Risk check error: {e}")

        # 3. Simulate Alert Hub Broadcast
        print("3. Testing Alert Hub Broadcast...")
        try:
            alert_resp = await client.post("http://alert-hub:8005/test-alert")
            if alert_resp.status_code == 200:
                print("   ✅ Alert broadcast queued successfully.")
            else:
                print(f"   ❌ Alert broadcast failed: {alert_resp.text}")
        except Exception as e:
            print(f"   ❌ Alert broadcast error: {e}")

    async def run(self):
        print(f"🚀 Initializing Master Test Suite v1.0 ({datetime.now().isoformat()})")
        await self.check_health()
        await self.verify_e2e_flow()
        print("\n--- Test Suite Complete ---")

if __name__ == "__main__":
    suite = MasterTestSuite()
    asyncio.run(suite.run())
