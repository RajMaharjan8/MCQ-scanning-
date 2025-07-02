import cv2
import numpy as np

ANSWER_KEY = {
    0: 0, 1: 2, 2: 2, 3: 2, 4: 3,
    5: 0, 6: 0, 7: 2, 8: 3, 9: 1,
    10: 2, 11: 0, 12: 2, 13: 1, 14: 3,
    15: 1, 16: 0, 17: 3, 18: 2, 19: 1
}
NUM_QUESTIONS = 20
NUM_CHOICES = 4

# Load and preprocess image
image = cv2.imread('mcqs.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
thresh = cv2.adaptiveThreshold(
    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
    cv2.THRESH_BINARY_INV, 11, 2)

# Bubble grid parameters (already calibrated)
bubble_centers = []
# Left column (Q1-Q10)
start_x, start_y = 68, 130
dx = 21
dy = 22
for q in range(10):
    row = []
    for c in range(NUM_CHOICES):
        x = start_x + c*dx
        y = start_y + q*dy
        row.append((x, y))
    bubble_centers.append(row)
# Right column (Q11-Q20)
start_x2, start_y2 = 336, 130
for q in range(10):
    row = []
    for c in range(NUM_CHOICES):
        x = start_x2 + c*dx
        y = start_y2 + q*dy
        row.append((x, y))
    bubble_centers.append(row)

# Marking and grading
score = 0
selected_answers = []
bubble_radius = 7  # Use the same as your debug circle

for q in range(NUM_QUESTIONS):
    max_fill = -1
    marked_choice = None
    for c in range(NUM_CHOICES):
        cx, cy = bubble_centers[q][c]
        # Extract a region around the bubble center
        roi = thresh[cy-bubble_radius:cy+bubble_radius, cx-bubble_radius:cx+bubble_radius]
        fill = np.sum(roi) // 255  # Count white pixels (filled area)
        if fill > max_fill:
            max_fill = fill
            marked_choice = c
    selected_answers.append(marked_choice)
    correct = ANSWER_KEY[q]
    print(f"Q{q+1}: Marked {chr(65+marked_choice)}, Correct {chr(65+correct)}", 
          "✓" if marked_choice == correct else "✗")
    if marked_choice == correct:
        score += 1

print("\nSelected answers (0=A, 1=B, 2=C, 3=D):")
print(selected_answers)
print(f"\nTotal Score: {score} / {NUM_QUESTIONS}")
