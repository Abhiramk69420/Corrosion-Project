import os
import csv
from datetime import datetime
from subprocess import run

import bme280
import smbus2

# -----------------------------
# BME280 Setup
# -----------------------------
PORT = 1
ADDRESS = 0x76        # Change to 0x77 if needed

bus = smbus2.SMBus(PORT)
calibration_params = bme280.load_calibration_params(bus, ADDRESS)

# -----------------------------
# Create folders
# -----------------------------
os.makedirs("images", exist_ok=True)
os.makedirs("data", exist_ok=True)

# -----------------------------
# Timestamp
# -----------------------------
timestamp = datetime.now()
time_string = timestamp.strftime("%Y-%m-%d %H:%M:%S")
image_name = timestamp.strftime("%Y%m%d_%H%M%S") + ".jpg"

# -----------------------------
# Read Sensor
# -----------------------------
data = bme280.sample(bus, ADDRESS, calibration_params)

temperature = round(data.temperature, 2)
humidity = round(data.humidity, 2)
pressure = round(data.pressure, 2)

# -----------------------------
# Take Picture
# -----------------------------
image_path = os.path.join("images", image_name)

run([
    "rpicam-still",
    "-o",
    image_path,
    "--nopreview"
])

# -----------------------------
# Save CSV
# -----------------------------
csv_file = "data/corrosion_data.csv"

file_exists = os.path.isfile(csv_file)

with open(csv_file, "a", newline="") as file:

    writer = csv.writer(file)

    if not file_exists:
        writer.writerow([
            "Timestamp",
            "Temperature_C",
            "Humidity_%",
            "Pressure_hPa",
            "Image"
        ])

    writer.writerow([
        time_string,
        temperature,
        humidity,
        pressure,
        image_name
    ])

print("--------------------------------")
print("Collection Complete")
print("--------------------------------")
print("Temperature:", temperature, "°C")
print("Humidity:", humidity, "%")
print("Pressure:", pressure, "hPa")
print("Image:", image_name)
