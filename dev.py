import subprocess
import sys
import os
import time
import signal
from pathlib import Path

# Configuration
PROJECT_ROOT = Path(__file__).parent
BACKEND_DIR = PROJECT_ROOT / "trading-ai-suite"
FRONTEND_DIR = BACKEND_DIR / "dashboard"

SERVICES = [
    {"name": "BrokerHub", "cmd": f"uvicorn broker_hub:app --port 8001", "cwd": BACKEND_DIR, "env": {"USE_MOCK_DATA": "true"}},
    {"name": "NewsHub", "cmd": f"uvicorn news_hub:app --port 8002", "cwd": BACKEND_DIR, "env": {"USE_MOCK_DATA": "true"}},
    {"name": "AI-Service", "cmd": f"uvicorn ai_service:app --port 8003", "cwd": BACKEND_DIR, "env": {"USE_MOCK_DATA": "true"}},
    {"name": "Risk-Engine", "cmd": f"uvicorn risk_engine:app --port 8004", "cwd": BACKEND_DIR, "env": {"USE_MOCK_DATA": "true"}},
    {"name": "Dashboard", "cmd": "npm run dev", "cwd": FRONTEND_DIR, "env": {}},
]

processes = []

def signal_handler(sig, frame):
    print("\n--- Shutting down all services... ---")
    for p in processes:
        p.terminate()
    print("👋 All services stopped.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    print("====================================")
    print("THE UPRISING : UNIFIED DEV LAUNCHER")
    print("MODE: MOCK (No API keys required)")
    print("====================================\n")

    # Start all services
    for service in SERVICES:
        print(f"🚀 Starting {service['name']}...")
        env = os.environ.copy()
        env.update(service.get("env", {}))
        
        try:
            p = subprocess.Popen(
                service["cmd"],
                shell=True,
                cwd=service["cwd"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            processes.append(p)
        except Exception as e:
            print(f"❌ Failed to start {service['name']}: {e}")

    print("\n✅ SYSTEM ONLINE")
    print("Frontend: http://localhost:3000")
    print("Press Ctrl+C to stop all services.\n")

    # Keep script running and proxy logs
    try:
        while True:
            for i, p in enumerate(processes):
                if p.poll() is not None:
                    print(f"⚠️ Service {SERVICES[i]['name']} died with code {p.returncode}")
                
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
