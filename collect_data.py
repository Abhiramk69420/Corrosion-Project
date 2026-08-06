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

MATERIAL = "steel"      # Change to aluminum, copper, stainless, etc.

PORT = 1
ADDRESS = 0x76          # Change to 0x77 if needed

# =====================================
# BME280 SETUP
# =====================================

bus = smbus2.SMBus(PORT)
calibration_params = bme280.load_calibration_params(bus, ADDRESS)

# =====================================
# CREATE FOLDERS
# =====================================

os.makedirs("data", exist_ok=True)

material_folder = os.path.join("images", MATERIAL)
os.makedirs(material_folder, exist_ok=True)

processed_folder = os.path.join("data", "processed")
os.makedirs(processed_folder, exist_ok=True)

# =====================================
# TIMESTAMP
# =====================================

timestamp = datetime.now()

time_string = timestamp.strftime("%Y-%m-%d %H:%M:%S")

image_name = timestamp.strftime("%Y%m%d_%H%M%S") + ".jpg"

image_path = os.path.join(material_folder, image_name)

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

run([
    "rpicam-still",
    "-o",
    image_path,
    "--nopreview"
])

# =====================================
# CREATE BASELINE IMAGE
# =====================================

baseline = os.path.join(material_folder, "baseline.jpg")

if not os.path.exists(baseline):
    shutil.copy(image_path, baseline)
    print("Baseline image created.")

# =====================================
# SAVE CSV
# =====================================

csv_file = "data/corrosion_data.csv"

file_exists = os.path.isfile(csv_file)

with open(csv_file, "a", newline="") as file:

    writer = csv.writer(file)

    if not file_exists:
        writer.writerow([
            "Timestamp",
            "Material",
            "Temperature_C",
            "Humidity_%",
            "Pressure_hPa",
            "Image"
        ])

    writer.writerow([
        time_string,
        MATERIAL,
        temperature,
        humidity,
        pressure,
        image_name
    ])

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
print("====================================")
