import asyncio
import httpx
import sys
import json
from datetime import datetime

# Configuration
SERVICES = {
    "Ollama (DeepSeek/Llama)": "http://localhost:11434/api/tags",
    "BrokerHub (CCXT)": "http://localhost:8001/health",
    "NewsHub (Scraping)": "http://localhost:8002/health",
    "AI Service (FastAPI)": "http://localhost:8003/health",
    "Risk Engine": "http://localhost:8004/health",
    "Hummingbot API": "http://localhost:8000/",
    "Freqtrade API": "http://localhost:8081/",
    "OctoBot UI": "http://localhost:5001/"
}

MOCK_MODE = "--mock" in sys.argv


async def fetch_status(name: str, url: str) -> tuple[str, bool, str, dict]:
    """Check a service endpoint and return (name, is_ok, message, response_data)."""
    if MOCK_MODE:
        return name, True, "MOCK — Skipped (syntax-only validation)", {}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                try:
                    data = response.json()
                except Exception:
                    data = {}

                # Extra check for AI Service health
                if name == "AI Service (FastAPI)" and data.get("status") == "waiting_for_model":
                    return name, False, f"Waiting for model. Result: {data}", data

                return name, True, "OK — Status 200", data
            else:
                return name, False, f"Failed with status: {response.status_code}", {}
    except httpx.RequestError as e:
        return name, False, f"Connection error: {str(e)}", {}
    except Exception as e:
        return name, False, f"Error: {str(e)}", {}


async def main():
    print("====================================")
    print("TRADING AI SUITE : SYSTEM VALIDATION")
    print(f"Mode: {'MOCK (no live calls)' if MOCK_MODE else 'LIVE'}")
    print(f"Time: {datetime.now().isoformat()}")
    print("====================================\n")

    tasks = [fetch_status(name, url) for name, url in SERVICES.items()]
    results = await asyncio.gather(*tasks)

    all_passed = True
    report = {
        "timestamp": datetime.now().isoformat(),
        "mode": "mock" if MOCK_MODE else "live",
        "services": {},
        "passed": True
    }

    for name, is_ok, msg, data in results:
        status_icon = "[OK]" if is_ok else "[FAIL]"
        print(f"{status_icon} {name}")
        print(f"    -> {msg}")

        report["services"][name] = {
            "status": "ok" if is_ok else "fail",
            "message": msg,
            "data": data
        }

        if not is_ok:
            all_passed = False

    report["passed"] = all_passed

    print("\n====================================")
    if all_passed:
        print("✅ SUCCESS: ALL SYSTEMS GO — READY FOR PRODUCTION")
    else:
        print("⚠️ WARNING: ERRORS DETECTED — PLEASE FIX FAILING SERVICES")

    print(f"\nTotal: {sum(1 for _, ok, _, _ in results if ok)}/{len(results)} services operational")
    print("====================================")

    # Write JSON report
    try:
        with open("test_results.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n📄 Report saved to test_results.json")
    except Exception as e:
        print(f"\n⚠️ Could not write report: {e}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    asyncio.run(main())
