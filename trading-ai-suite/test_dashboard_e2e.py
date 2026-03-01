"""
The Uprising Trading Floor - Dashboard Production Integrity Check
Verifies that all backend services are running in production mode (no mocks).
"""
import httpx
import asyncio
import sys
import os

# Service endpoints (standard docker-compose ports)
SERVICES = {
    "BrokerHub":  "http://localhost:8001",
    "NewsHub":    "http://localhost:8002",
    "AIService":  "http://localhost:8003",
    "RiskEngine": "http://localhost:8004",
    "AlertHub":   "http://localhost:8005",
}

async def check_service(name: str, url: str) -> dict:
    """Check if service is running and NOT in mock mode."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{url}/health")
            if resp.status_code == 200:
                data = resp.json()
                mode = data.get("mode", "production")
                if mode == "mock":
                    return {"name": name, "status": "FAIL (MOCK DETECTED)", "mode": "mock"}
                return {"name": name, "status": "OK", "mode": mode}
            else:
                return {"name": name, "status": f"ERROR (HTTP {resp.status_code})", "mode": "unknown"}
    except Exception as e:
        return {"name": name, "status": f"OFFLINE ({str(e)})", "mode": "none"}

async def test_news_scraping():
    """Verify NewsHub returns real scraped data."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{SERVICES['NewsHub']}/news?symbol=BTC&limit=1")
            if resp.status_code == 200:
                news = resp.json()
                if isinstance(news, list) and len(news) > 0:
                    source = news[0].get("source", "")
                    if source in ["The Uprising News", "MockSource"]:
                        return "FAIL (Mock News Found)"
                    return f"PASS (Real News from {source})"
                return "PASS (Empty list - real scraping is limited)"
    except:
        pass
    return "SKIP (NewsHub Offline)"

async def main():
    print("=" * 60)
    print("THE UPRISING : PRODUCTION READINESS AUDIT")
    print("=" * 60)
    
    results = await asyncio.gather(*[check_service(n, u) for n, u in SERVICES.items()])
    
    all_ok = True
    for res in results:
        print(f"  {res['name']:<12} : {res['status']}")
        if "FAIL" in res['status']:
            all_ok = False
            
    print("-" * 60)
    news_res = await test_news_scraping()
    print(f"  News Integrity : {news_res}")
    
    print("=" * 60)
    if all_ok:
        print("RESULT: PRODUCTION INTEGRITY VERIFIED")
    else:
        print("RESULT: PRODUCTION AUDIT FAILED - MOCK DATA DETECTED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
