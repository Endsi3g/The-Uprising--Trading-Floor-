import json
import os
import asyncio
from pathlib import Path
from ai_feedback_loop import AIFeedbackLoop
from param_optimizer import ParamOptimizer

# Paths
TRADING_STATS_FILE = Path("trading_performance.json")
CONFIG_FILE = Path("freqtrade/user_data/config.json")
PROMPT_FILE = Path("ai_system_prompt.txt")

async def test_feedback_loop():
    print("Testing AI Feedback Loop...")
    # Inject high drawdown to trigger defensive prompt
    with open(TRADING_STATS_FILE, "w") as f:
        json.dump({"win_rate": 0.5, "max_drawdown": 0.15}, f)
    
    loop = AIFeedbackLoop()
    # Mocking the file path in the loop to be local for the test if needed
    # (Since the script runs from trading-ai-suite root in production)
    loop.analyze_logs()
    loop.tune_prompt()
    
    if PROMPT_FILE.exists():
        with open(PROMPT_FILE, "r") as f:
            content = f.read()
            print(f"Generated Prompt: {content[:100]}...")
            if "DEFENSIVE" in content:
                print("[SUCCESS] Feedback loop triggered defensive mode correctly.")
            else:
                print("[FAILURE] Feedback loop failed to trigger defensive mode.")
    else:
        print("[FAILURE] Prompt file not created.")

async def test_param_optimizer():
    print("\nTesting Parameter Optimizer...")
    # Ensure config exists
    if not CONFIG_FILE.exists():
        print(f"[FAILURE] Config file not found at {CONFIG_FILE}. Skipping test.")
        return

    optimizer = ParamOptimizer()
    # Mock volatility to 'High'
    optimizer.current_volatility = "High"
    optimizer.optimize_params()
    
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
        stoploss = config.get("stoploss")
        trades = config.get("max_open_trades")
        print(f"Updated Config - Stoploss: {stoploss}, Max Open Trades: {trades}")
        if stoploss == -0.05 and trades == 3:
            print("[SUCCESS] Parameter optimizer updated config correctly for High volatility.")
        else:
            print("[FAILURE] Parameter optimizer failed to update config correctly.")

async def main():
    await test_feedback_loop()
    await test_param_optimizer()

if __name__ == "__main__":
    asyncio.run(main())
