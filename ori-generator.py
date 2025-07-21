import sys
import cv2
import numpy as np
import json

def crop_inside_border(image_path, output_path="cropped_bottom_half.jpg", debug_output_path="bubble_centers_debug.jpg"):
    image = cv2.imread(image_path)
    if image is None:
        return {"error": f"Could not load image {image_path}"}

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if 5 < w < 50 and 5 < h < 50:
            boxes.append((x, y, x + w, y + h))

    if len(boxes) < 4:
        return {"error": "Not enough alignment markers detected."}

    x_min = min(box[0] for box in boxes)
    y_min = min(box[1] for box in boxes)
    x_max = max(box[2] for box in boxes)
    y_max = max(box[3] for box in boxes)

    margin = 10
    x_min += margin
    y_min += margin
    x_max -= margin
    y_max -= margin

    # Crop full inside region
    full_crop = image[y_min:y_max, x_min:x_max]

    # Get only bottom half
    height = full_crop.shape[0]
    bottom_half = full_crop[height // 2:, :]
    cv2.imwrite(output_path, bottom_half)

    # ======= Draw BUBBLE COORDINATES on bottom_half ==========
    NUM_ROWS = 10
    NUM_COLS = 5
    NUM_CHOICES = 4
    bubble_radius = 14

    lh, lw = bottom_half.shape[:2]  # Get height (lh) and width (lw) of the bottom half image

    start_x = int(0.08 * lw)       # Starting X coordinate (horizontal offset) for the first bubble in a column (A option of Q1)
    start_y = int(0.235 * lh)       # Starting Y coordinate (vertical offset) for the first row of bubbles (row for Q1)

    dx = int(0.041 * lw)           # Horizontal distance between choices (A → B → C → D)
    dy = int(0.067 * lh)            # Vertical distance between rows (Q1 → Q2 → Q3...)

    col_offset = int(0.187 * lw)    # Horizontal distance between question columns (e.g., Q1–10 column to Q11–20 column)

    bubble_centers = []
    for col in range(NUM_COLS):
        x_offset = start_x + col * col_offset
        for row in range(NUM_ROWS):
            y = start_y + row * dy
            row_centers = []
            for choice in range(NUM_CHOICES):
                x = x_offset + choice * dx
                row_centers.append((int(x), int(y)))
            bubble_centers.append(row_centers)

    debug_img = bottom_half.copy()
    for row in bubble_centers:
        for (x, y) in row:
            cv2.circle(debug_img, (x, y), bubble_radius, (0, 0, 255), 2)

    cv2.imwrite(debug_output_path, debug_img)

    return {
        "message": "Successfully cropped and marked bubble centers.",
        "cropped_img": output_path,
        "debug_img": debug_output_path,
        "crop_box": [x_min, y_min + height // 2, x_max, y_max],
        "total_questions": NUM_ROWS * NUM_COLS,
        "total_choices_per_question": NUM_CHOICES
    }

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python crop_and_mark_bubbles.py <image_path>"}))
        sys.exit(1)

    image_path = sys.argv[1]
    result = crop_inside_border(image_path)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
