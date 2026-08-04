import time
import subprocess

INTERVAL = 36  # seconds (1 hour)

print("Corrosion Monitor Started")

while True:
    print("Collecting data...")
    subprocess.run(["python", "collect_data.py"])
    print(f"Waiting {INTERVAL} seconds...")
    time.sleep(INTERVAL)
