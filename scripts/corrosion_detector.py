import os
import csv
from datetime import datetime

import cv2
import numpy as np

# =====================================
# SETTINGS
# =====================================

MATERIAL = "steel"

# Difference threshold: higher values ignore small lighting changes.
DIFF_THRESHOLD = 30

# Minimum contour size for the annotated image.
MIN_CONTOUR_AREA = 40

# =====================================
# PROJECT PATHS
# =====================================

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IMAGE_FOLDER = os.path.join(PROJECT_ROOT, "images", MATERIAL)
PROCESSED_FOLDER = os.path.join(PROJECT_ROOT, "data", "processed")

os.makedirs(PROCESSED_FOLDER, exist_ok=True)

BASELINE_PATH = os.path.join(IMAGE_FOLDER, "baseline.jpg")

# =====================================
# CHECK BASELINE
# =====================================

if not os.path.exists(BASELINE_PATH):
    print("No baseline image found.")
    print("Run collect_data.py first.")
    raise SystemExit(1)

# =====================================
# FIND NEWEST IMAGE
# =====================================

images = sorted(
    [
        filename
        for filename in os.listdir(IMAGE_FOLDER)
        if filename.lower().endswith(".jpg")
        and filename != "baseline.jpg"
        and not filename.endswith("_analysis.jpg")
    ]
)

if not images:
    print("No new images found.")
    raise SystemExit(0)

latest_image = images[-1]
latest_path = os.path.join(IMAGE_FOLDER, latest_image)

# =====================================
# LOAD IMAGES
# =====================================

baseline = cv2.imread(BASELINE_PATH)
current = cv2.imread(latest_path)

if baseline is None or current is None:
    print("Unable to load baseline or current image.")
    raise SystemExit(1)

# Use the same resolution for both images.
baseline = cv2.resize(baseline, (640, 480))
current = cv2.resize(current, (640, 480))

# Slight blur reduces tiny camera/noise differences.
baseline_blur = cv2.GaussianBlur(baseline, (5, 5), 0)
current_blur = cv2.GaussianBlur(current, (5, 5), 0)

# =====================================
# 1. SURFACE CHANGE SCORE
# =====================================

difference = cv2.absdiff(baseline_blur, current_blur)
gray_difference = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

_, threshold = cv2.threshold(
    gray_difference,
    DIFF_THRESHOLD,
    255,
    cv2.THRESH_BINARY,
)

# Remove small isolated noise.
kernel = np.ones((3, 3), np.uint8)
threshold = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel)
threshold = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)

changed_pixels = np.count_nonzero(threshold)
total_pixels = threshold.size

changed_surface_percent = (changed_pixels / total_pixels) * 100

# =====================================
# 2. RUST-COLOR SCORE
# =====================================
#
# This is a simple visual indicator, not a laboratory corrosion
# measurement. It looks for reddish/brown pixels commonly associated
# with visible rust on steel.

hsv = cv2.cvtColor(current_blur, cv2.COLOR_BGR2HSV)

lower_rust = np.array([5, 60, 40])
upper_rust = np.array([25, 255, 220])

rust_mask = cv2.inRange(hsv, lower_rust, upper_rust)

rust_pixels = np.count_nonzero(rust_mask)
rust_percent = (rust_pixels / total_pixels) * 100

# =====================================
# 3. COMBINED CORROSION SCORE
# =====================================
#
# The score is a project-specific visual index from 0-100.
# It should be calibrated against your actual experiment.

corrosion_score = (
    0.70 * changed_surface_percent
    + 0.30 * rust_percent
)

corrosion_score = min(corrosion_score, 100.0)

# =====================================
# DRAW CHANGES
# =====================================

contours, _ = cv2.findContours(
    threshold,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE,
)

output = current.copy()

for contour in contours:
    if cv2.contourArea(contour) > MIN_CONTOUR_AREA:
        x, y, width, height = cv2.boundingRect(contour)

        cv2.rectangle(
            output,
            (x, y),
            (x + width, y + height),
            (0, 0, 255),
            2,
        )

# Add score information to the image.
cv2.putText(
    output,
    f"Corrosion Score: {corrosion_score:.2f}%",
    (10, 30),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.7,
    (0, 0, 255),
    2,
)

# =====================================
# SAVE ANALYSIS IMAGE
# =====================================

output_name = latest_image.replace(".jpg", "_analysis.jpg")
output_path = os.path.join(PROCESSED_FOLDER, output_name)

cv2.imwrite(output_path, output)

# =====================================
# SAVE CORROSION DATA
# =====================================

csv_file = os.path.join(PROJECT_ROOT, "data", "corrosion_scores.csv")
exists = os.path.isfile(csv_file)

with open(csv_file, "a", newline="") as file:
    writer = csv.writer(file)

    if not exists:
        writer.writerow(
            [
                "Timestamp",
                "Material",
                "Image",
                "ChangedSurface_%",
                "RustPixels_%",
                "CorrosionScore_%",
            ]
        )

    writer.writerow(
        [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            MATERIAL,
            latest_image,
            round(changed_surface_percent, 2),
            round(rust_percent, 2),
            round(corrosion_score, 2),
        ]
    )

# =====================================
# SUMMARY
# =====================================

print("--------------------------------")
print(" Corrosion Analysis Complete")
print("--------------------------------")
print(f"Material:             {MATERIAL}")
print(f"Image:                {latest_image}")
print(f"Changed surface:      {changed_surface_percent:.2f}%")
print(f"Rust-colored pixels:  {rust_percent:.2f}%")
print(f"Corrosion score:      {corrosion_score:.2f}%")
print(f"Analysis image:       {output_path}")
print("--------------------------------")
