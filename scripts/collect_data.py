import os
import csv
import shutil
from datetime import datetime
from subprocess import run

import bme280
import smbus2

# =====================================
# SETTINGS
# =====================================

MATERIAL = "steel"  # Change to aluminum, copper, stainless, etc.

PORT = 1
ADDRESS = 0x76  # Change to 0x77 if your BME280 uses that address

# =====================================
# PROJECT PATHS
# =====================================

# This makes the script work even when launched from the scripts folder.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_FOLDER = os.path.join(PROJECT_ROOT, "data")
IMAGE_FOLDER = os.path.join(PROJECT_ROOT, "images")
MATERIAL_FOLDER = os.path.join(IMAGE_FOLDER, MATERIAL)
PROCESSED_FOLDER = os.path.join(DATA_FOLDER, "processed")

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(MATERIAL_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# =====================================
# BME280 SETUP
# =====================================

bus = smbus2.SMBus(PORT)
calibration_params = bme280.load_calibration_params(bus, ADDRESS)

# =====================================
# TIMESTAMP
# =====================================

timestamp = datetime.now()
time_string = timestamp.strftime("%Y-%m-%d %H:%M:%S")

image_name = timestamp.strftime("%Y%m%d_%H%M%S") + ".jpg"
image_path = os.path.join(MATERIAL_FOLDER, image_name)

# =====================================
# READ SENSOR
# =====================================

data = bme280.sample(bus, ADDRESS, calibration_params)

temperature = round(data.temperature, 2)
humidity = round(data.humidity, 2)
pressure = round(data.pressure, 2)

# =====================================
# TAKE PICTURE
# =====================================

result = run(
    [
        "rpicam-still",
        "-o",
        image_path,
        "--nopreview",
        "--width",
        "640",
        "--height",
        "480",
    ],
    check=True,
)

# =====================================
# CREATE BASELINE IMAGE
# =====================================

baseline_path = os.path.join(MATERIAL_FOLDER, "baseline.jpg")

if not os.path.exists(baseline_path):
    shutil.copy2(image_path, baseline_path)
    print("Baseline image created.")

# =====================================
# SAVE SENSOR DATA
# =====================================

csv_file = os.path.join(DATA_FOLDER, "corrosion_data.csv")
file_exists = os.path.isfile(csv_file)

with open(csv_file, "a", newline="") as file:
    writer = csv.writer(file)

    if not file_exists:
        writer.writerow(
            [
                "Timestamp",
                "Material",
                "Temperature_C",
                "Humidity_%",
                "Pressure_hPa",
                "Image",
                "ImagePath",
            ]
        )

    writer.writerow(
        [
            time_string,
            MATERIAL,
            temperature,
            humidity,
            pressure,
            image_name,
            os.path.join("images", MATERIAL, image_name),
        ]
    )

# =====================================
# SUMMARY
# =====================================

print("\n====================================")
print(" Collection Complete")
print("====================================")
print(f"Material:    {MATERIAL}")
print(f"Temperature: {temperature:.2f} °C")
print(f"Humidity:    {humidity:.2f} %")
print(f"Pressure:    {pressure:.2f} hPa")
print(f"Image:       {image_name}")
print(f"Saved to:    {image_path}")
print("====================================")
