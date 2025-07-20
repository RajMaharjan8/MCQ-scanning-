import cv2
import numpy as np

# Parameters for your answer region and grid
NUM_ROWS = 10
NUM_COLS = 5
NUM_CHOICES = 4
bubble_radius = 9  # after resizing to 1000px wide
resize_width = 1000  # normalize all inputs

# Load image and resize
image = cv2.imread('data.png')
if image is None:
    raise FileNotFoundError("Couldn't load 'data.png'")
h0, w0 = image.shape[:2]
aspect = h0 / w0
image = cv2.resize(image, (resize_width, int(resize_width * aspect)))
h, w = image.shape[:2]

# ----- Divide into upper/lower -----
# For your attached sheet, lower grid starts at ~60% height
lower_frac = 0.60
upper_part = image[:int(h*lower_frac), :]
lower_part = image[int(h*lower_frac):, :]

# ----- BUBBLE GRID, NORMALIZED to resized lower part -----
# Now, all positions can be fixed for the resized img
lh, lw = lower_part.shape[:2]

# These can be tuned; these work for your attached image after resizing!
start_x = int(0.115 * lw)
start_y = int(0.01 * lh)
dx = int(0.0389 * lw)          # horizontal gap between choices
dy = int(0.077 * lh)         # vertical gap between rows
col_offset = int(0.167 * lw)  # offset between each 10-question column

bubble_centers = []
for col in range(NUM_COLS):
    x_offset = start_x + col * col_offset
    for row in range(NUM_ROWS):
        y = start_y + row * dy
        this_q = []
        for c in range(NUM_CHOICES):
            x = x_offset + c * dx
            this_q.append((x, y))
        bubble_centers.append(this_q)

# ----- DEBUG DRAW -----
debug = lower_part.copy()
for row in bubble_centers:
    for (x, y) in row:
        cv2.circle(debug, (int(x), int(y)), bubble_radius, (0, 0, 255), 2)
cv2.imwrite('bubble_centers_debug.jpg', debug)
print("Normalized & marked bubbles saved as bubble_centers_debug.jpg")
