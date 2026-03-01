import os
import sys
import unittest
import asyncio
import importlib.util
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

class TestUprisingSuiteIntegrity(unittest.TestCase):
    """Integrity tests for The Uprising Trading Floor codebase."""

    def test_directory_structure(self):
        """Verify that mandatory directories exist."""
        required_dirs = ["docs", "bin", "trading-ai-suite", "hummingbot", "skills"]
        for d in required_dirs:
            with self.subTest(directory=d):
                self.assertTrue((ROOT_DIR / d).is_dir(), f"Missing mandatory directory: {d}")

    def test_critical_files(self):
        """Verify that core configuration and documentation files exist."""
        required_files = [
            "README.md",
            "Dockerfile",
            "docker-compose.yml",
            "pyproject.toml",
            "docs/AI_MANDATORY_INSTRUCTIONS.md"
        ]
        for f in required_files:
            with self.subTest(file=f):
                self.assertTrue((ROOT_DIR / f).is_file(), f"Missing critical file: {f}")

    def test_bin_scripts_permissions(self):
        """Ensure scripts in bin/ are present."""
        scripts = ["install", "start", "clean"]
        for s in scripts:
            script_path = ROOT_DIR / "bin" / s
            self.assertTrue(script_path.exists(), f"Missing script in bin/: {s}")

    def test_ai_suite_health_script(self):
        """Verify that the AI suite verification script is present and importable."""
        health_script = ROOT_DIR / "trading-ai-suite" / "test_system.py"
        self.assertTrue(health_script.exists())
        
        # Try to import it (or at least check syntax)
        spec = importlib.util.spec_from_file_location("test_system", health_script)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            self.assertTrue(hasattr(module, 'SERVICES'), "test_system.py missing SERVICES registry")
        except Exception as e:
            self.fail(f"Failed to load test_system.py: {e}")

async def run_live_service_check():
    """Run the existing live service check in mock mode."""
    health_script_path = ROOT_DIR / "trading-ai-suite" / "test_system.py"
    if health_script_path.exists():
        print("\n--- Running AI Suite Service Registry Check (Mock Mode) ---")
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(health_script_path), "--mock",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
    try:
        print(stdout.decode('utf-8'))
    except UnicodeDecodeError:
        print(stdout.decode('cp1252', errors='replace'))
        if process.returncode != 0:
            print(f"Error: {stderr.decode()}")
            return False
        return True
    return False

if __name__ == "__main__":
    print("====================================")
    print("THE UPRISING : MASTER INTEGRITY TEST")
    print(f"Root: {ROOT_DIR}")
    print("====================================\n")
    
    # Run unittest suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUprisingSuiteIntegrity)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Run async service check
    service_ok = asyncio.run(run_live_service_check())
    
    if result.wasSuccessful() and service_ok:
        print("\n✅ ALL INTEGRITY CHECKS PASSED")
        sys.exit(0)
    else:
        print("\n❌ SOME CHECKS FAILED")
        sys.exit(1)
