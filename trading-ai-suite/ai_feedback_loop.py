import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime

# Configuration
LOG_DIR = Path("logs")
TRADING_STATS_FILE = Path("trading_performance.json")
AI_SYSTEM_PROMPT_FILE = Path("ai_system_prompt.txt")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AIFeedbackLoop")

class AIFeedbackLoop:
    def __init__(self):
        self.stats = self._load_stats()
        
    def _load_stats(self):
        if TRADING_STATS_FILE.exists():
            try:
                with open(TRADING_STATS_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading stats: {e}")
        return {"total_trades": 0, "win_rate": 0.0, "avg_profit": 0.0, "recent_losses": 0, "max_drawdown": 0.0}

    def analyze_logs(self):
        """Analyzes performance metrics to identify improvement areas."""
        logger.info("Analyzing trading performance...")
        self.stats = self._load_stats() # Refresh stats
        
        # In a real scenario, we'd also parse actual execution logs here.
        perf_summary = (
            f"Win Rate: {self.stats.get('win_rate', 0)*100:.1f}%, "
            f"Drawdown: {self.stats.get('max_drawdown', 0)*100:.1f}%"
        )
        logger.info(f"Performance Summary: {perf_summary}")
        
    def tune_prompt(self):
        """Generates an optimized system prompt based on performance data."""
        logger.info("Tuning AI system prompt based on metrics...")
        
        base_prompt = "You are a Senior Quantitative Trader for 'The Uprising'."
        win_rate = self.stats.get('win_rate', 0.5)
        drawdown = self.stats.get('max_drawdown', 0.0)
        
        directives = []
        if drawdown > 0.10:
            directives.append("URGENT: Max drawdown exceeded 10%. Switch to DEFENSIVE mode. Stop all high-risk arbitrage. Prioritize USDT preservation.")
        elif win_rate < 0.45:
            directives.append("ADVISORY: Win rate is below 45%. Tighten entry criteria. Require stronger trend confirmation before execution.")
        else:
            directives.append("OPTIMAL: Performance is stable. Identify high-alpha opportunities and maintain balanced portfolio distribution.")

        final_prompt = f"{base_prompt} { ' '.join(directives) } Ensure execution remains logic-driven and emotion-free."
        
        with open(AI_SYSTEM_PROMPT_FILE, "w") as f:
            f.write(final_prompt)
        
        logger.info(f"New system prompt deployed (Win Rate: {win_rate*100:.1f}%)")

    def run(self):
        logger.info("AI Feedback Loop started.")
        while True:
            self.analyze_logs()
            self.tune_prompt()
            # In production this might run every 4 hours. For demo, every 30s.
            time.sleep(30)

if __name__ == "__main__":
    loop = AIFeedbackLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        logger.info("Feedback loop stopped.")
