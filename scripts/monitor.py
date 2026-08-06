import time
import subprocess
from datetime import datetime

# Time between measurements (seconds)
# INTERVAL = 3600      # 1 hour
 INTERVAL = 60      # Use this while testing

print("=" * 50)
print(" Smart Corrosion Monitor Started ")
print("=" * 50)

while True:
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Collecting data...")

    try:
        subprocess.run(["python3", "scripts/collect_data.py"], check=True)
	
	subprocess.run(["python3","scripts/corrosion_detector.py"], check=True)

        print("✓ Data collection complete")

    except subprocess.CalledProcessError as e:
        print(f"✗ Error running collect_data.py: {e}")

    print(f"Sleeping for {INTERVAL} seconds...\n")
    time.sleep(INTERVAL)
