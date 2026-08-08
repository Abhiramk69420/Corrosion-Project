import os
import time
import subprocess
from datetime import datetime

# =====================================
# SETTINGS
# =====================================

# 60 seconds is useful for testing.
# Change to 3600 for one measurement per hour.
INTERVAL = 60

# =====================================
# PROJECT PATHS
# =====================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLLECT_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "collect_data.py")
DETECTOR_SCRIPT = os.path.join(PROJECT_ROOT, "scripts", "corrosion_detector.py")

print("=" * 50)
print(" Smart Corrosion Monitor Started ")
print("=" * 50)
print(f"Measurement interval: {INTERVAL} seconds")
print("Press Ctrl+C to stop.")
print("=" * 50)

try:
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Starting measurement...")

        try:
            # 1. Collect BME280 data and take a picture.
            subprocess.run(
                ["python3", COLLECT_SCRIPT],
                check=True,
            )

            # 2. Analyze the newest picture.
            subprocess.run(
                ["python3", DETECTOR_SCRIPT],
                check=True,
            )

            print("✓ Collection and corrosion analysis complete")

        except subprocess.CalledProcessError as error:
            print(f"✗ A monitoring step failed: {error}")

        print(f"Sleeping for {INTERVAL} seconds...")
        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\n\nSmart Corrosion Monitor stopped.")
