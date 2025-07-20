import sys
import json
import cv2
import numpy as np

def process_answer_sheet(image_path):
    # Parameters for the bubble grid
    NUM_ROWS = 10
    NUM_COLS = 5
    NUM_CHOICES = 4
    bubble_radius = 10  # size of drawn circles, tune as needed
    resize_width = 1000  # to normalize input sizes

    # Load and resize the original image
    image = cv2.imread(image_path)
    if image is None:
        return {"error": "Couldn't load image from path: " + image_path}

    h0, w0 = image.shape[:2]
    aspect = h0 / w0
    image_resized = cv2.resize(image, (resize_width, int(resize_width * aspect)))
    h, w = image_resized.shape[:2]

    # Crop the lower part (approx 60%)
    lower_frac = 0.55
    lower_part = image_resized[int(h * lower_frac):, :]

    lh, lw = lower_part.shape[:2]

    # Calculate bubble centers relative to the resized lower part
    start_x = int(0.115 * lw)
    start_y = int(0.12 * lh)
    dx = int(0.0389 * lw)          # horizontal gap between choices (A,B,C,D)
    dy = int(0.069 * lh)           # vertical gap between rows
    col_offset = int(0.167 * lw)   # horizontal gap between question columns

    bubble_centers = []
    for col in range(NUM_COLS):
        x_offset = start_x + col * col_offset
        for row in range(NUM_ROWS):
            y = start_y + row * dy
            this_row_centers = []
            for choice in range(NUM_CHOICES):
                x = x_offset + choice * dx
                this_row_centers.append((int(x), int(y)))
            bubble_centers.append(this_row_centers)

    # Draw debug circles on the lower part for all bubbles
    debug_img = lower_part.copy()
    for row_centers in bubble_centers:
        for (x, y) in row_centers:
            cv2.circle(debug_img, (x, y), bubble_radius, (0, 0, 255), 2)  # red circles

    # Save the debug image
    debug_output_path = "bubble_centers_debug.jpg"
    cv2.imwrite(debug_output_path, debug_img)

    # Return JSON result including the debug image filename (adjust if needed)
    return {
        "message": "Processed image and marked bubble centers",
        "debug_image": debug_output_path,
        "total_questions": NUM_ROWS * NUM_COLS,
        "total_choices_per_question": NUM_CHOICES
    }

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python ori_pt1.py <image_path>"}))
        sys.exit(1)

    image_path = sys.argv[1]
    result = process_answer_sheet(image_path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
