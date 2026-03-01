import os
import json
import httpx
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Configuration
TRADING_STATS_FILE = Path("trading_performance.json")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8003/ai/analyze")
ALERT_HUB_URL = os.getenv("ALERT_HUB_URL", "http://alert-hub:8005/alerts")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PerformanceRecap")

class PerformanceRecap:
    def __init__(self):
        self.stats = self._load_stats()

    def _load_stats(self):
        if TRADING_STATS_FILE.exists():
            with open(TRADING_STATS_FILE, "r") as f:
                return json.load(f)
        return {}

    async def generate_report(self):
        if not self.stats:
            logger.error("No trading stats found. Cannot generate report.")
            return

        logger.info("Requesting AI performance analysis...")
        
        context = json.dumps(self.stats, indent=2)
        instruction = (
            "Analyse ces statistiques de trading de la semaine. "
            "Genere un rapport '12-year-old simple' (tres facile a comprendre). "
            "Inclus: 1. Resume global (ca va bien ou pas?), 2. Le point fort, 3. Ce qu'on doit ameliorer. "
            "Utilise un ton encourageant mais pro. Reponds en Francais."
        )

        payload = {
            "context": context,
            "instruction": instruction
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(AI_SERVICE_URL, json=payload)
                if resp.status_code == 200:
                    analysis = resp.json().get("response", "No analysis provided.")
                    self._save_report(analysis)
                    await self._broadcast_report(analysis)
                else:
                    logger.error(f"AI Service error: {resp.text}")
        except Exception as e:
            logger.error(f"Failed to generate AI report: {e}")

    def _save_report(self, analysis):
        date_str = datetime.now().strftime("%Y-%m-%d")
        report_file = Path(f"reports/performance_recap_{date_str}.md")
        report_file.parent.mkdir(exist_ok=True)
        
        content = f"# 📊 Recapitulatif Hebdomadaire - {date_str}\n\n"
        content += analysis
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Report saved to {report_file}")

    async def _broadcast_report(self, analysis):
        """Sends a condensed version of the report to Alert Hub."""
        logger.info("Broadcasting report to Alert Hub...")
        condensed = analysis[:500] + "..." if len(analysis) > 500 else analysis
        
        alert_payload = {
            "source": "WeeklyRecap",
            "message": f"✨ Nouveau rapport de performance disponible !\n\n{condensed}",
            "severity": "INFO"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(ALERT_HUB_URL, json=alert_payload)
        except Exception as e:
            logger.error(f"Broadcasting failed: {e}")

async def main():
    recap = PerformanceRecap()
    await recap.generate_report()

if __name__ == "__main__":
    asyncio.run(main())
