import cv2
import numpy as np

# Load your image
image = cv2.imread('new.png')

# Parameters: adjust these for your specific sheet!
NUM_ROWS = 20
NUM_COLS = 5
NUM_CHOICES = 4
bubble_radius = 11  # adjust as needed

# Top-left corner of first bubble in first column
start_x, start_y = 125, 100  # Example values; calibrate for your sheet!
dx = 33                  # Horizontal distance between choices (A-B, B-C, etc.)
dy = 33                    # Vertical distance between rows
col_offset = 183             # Horizontal distance between columns (columns of questions)

bubble_centers = []
for col in range(NUM_COLS):
    col_centers = []
    x_offset = start_x + col * col_offset
    for row in range(NUM_ROWS):
        row_centers = []
        y = start_y + row * dy
        for c in range(NUM_CHOICES):
            x = x_offset + c * dx
            row_centers.append((x, y))
        bubble_centers.append(row_centers)

# Draw debug image
debug_img = image.copy()
for row in bubble_centers:
    for (x, y) in row:
        cv2.circle(debug_img, (x, y), bubble_radius, (0, 0, 255), 2)
cv2.imwrite('bubble_centers_debug.jpg', debug_img)
print("Bubble centers image saved as bubble_centers_debug.jpg")
