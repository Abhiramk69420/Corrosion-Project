import os
import csv
from datetime import datetime

import cv2
import numpy as np

# ===========================
# SETTINGS
# ===========================

MATERIAL = "steel"

image_folder = os.path.join("images", MATERIAL)
processed_folder = os.path.join("data", "processed")

os.makedirs(processed_folder, exist_ok=True)

baseline_path = os.path.join(image_folder, "baseline.jpg")

# ===========================
# FIND NEWEST IMAGE
# ===========================

images = sorted([
    f for f in os.listdir(image_folder)
    if f.endswith(".jpg") and f != "baseline.jpg"
])

if len(images) == 0:
    print("No images found.")
    quit()

latest_image = images[-1]

latest_path = os.path.join(image_folder, latest_image)

# ===========================
# LOAD IMAGES
# ===========================

baseline = cv2.imread(baseline_path)
current = cv2.imread(latest_path)

if baseline is None or current is None:
    print("Unable to load images.")
    quit()

baseline = cv2.resize(baseline, (640,480))
current = cv2.resize(current, (640,480))

# ===========================
# DIFFERENCE IMAGE
# ===========================

difference = cv2.absdiff(baseline, current)

gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

_, thresh = cv2.threshold(gray,25,255,cv2.THRESH_BINARY)

changed_pixels = np.count_nonzero(thresh)
total_pixels = thresh.size

corrosion_score = (changed_pixels / total_pixels) * 100

# ===========================
# DRAW CHANGES
# ===========================

contours, _ = cv2.findContours(
    thresh,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)

output = current.copy()

for contour in contours:

    if cv2.contourArea(contour) > 40:

        x,y,w,h = cv2.boundingRect(contour)

        cv2.rectangle(
            output,
            (x,y),
            (x+w,y+h),
            (0,0,255),
            2
        )

# ===========================
# SAVE IMAGE
# ===========================

output_name = latest_image.replace(".jpg","_analysis.jpg")

output_path = os.path.join(processed_folder, output_name)

cv2.imwrite(output_path, output)

# ===========================
# SAVE CSV
# ===========================

csv_file = "data/corrosion_scores.csv"

exists = os.path.isfile(csv_file)

with open(csv_file,"a",newline="") as file:

    writer = csv.writer(file)

    if not exists:

        writer.writerow([
            "Timestamp",
            "Material",
            "Image",
            "CorrosionScore"
        ])

    writer.writerow([
        datetime.now(),
        MATERIAL,
        latest_image,
        round(corrosion_score,2)
    ])

print("--------------------------------")
print("Corrosion Analysis Complete")
print("--------------------------------")
print("Material:", MATERIAL)
print("Image:", latest_image)
print("Corrosion Score:", round(corrosion_score,2),"%")
print("Annotated image saved to:")
print(output_path)
