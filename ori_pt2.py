import sys
import json
import cv2
import numpy as np

# Constants
ANSWER_KEY = {
    0: 3, 1: 2, 2: 1, 3: 1, 4: 1,
    5: 2, 6: 3, 7: 0, 8: 2, 9: 3,
    10: 3, 11: 1, 12: 2, 13: 1, 14: 3,
    15: 2, 16: 2, 17: 0, 18: 1, 19: 2,
    20: 3, 21: 0, 22: 0, 23: 2, 24: 1,
    25: 3, 26: 2, 27: 0, 28: 2, 29: 1,
    30: 1, 31: 2, 32: 0, 33: 1, 34: 0,
    35: 3, 36: 2, 37: 1, 38: 2, 39: 0,
    40: 1, 41: 2, 42: 3, 43: 1, 44: 1,
    45: 2, 46: 2, 47: 3, 48: 0, 49: 1,
}

NUM_ROWS = 20
NUM_COLS = 5
NUM_CHOICES = 4
BUBBLE_RADIUS = 10

MIN_FILL = 150
MIN_DIFF = 60

def process_answer_sheet(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return {"error": f"Could not load image at path {image_path}"}

    # Resize
    RESIZE_WIDTH = 1000
    h0, w0 = image.shape[:2]
    aspect_ratio = h0 / w0
    resized_height = int(RESIZE_WIDTH * aspect_ratio)
    image_resized = cv2.resize(image, (RESIZE_WIDTH, resized_height))
    h, w = image_resized.shape[:2]

    # Crop answer area (usually lower half)
    lower_frac = 0.55
    lower_part = image_resized[int(h * lower_frac):, :]
    lh, lw = lower_part.shape[:2]

    # Grid positions
    start_x = int(0.110 * lw)
    start_y = int(0.22 * lh)
    dx = int(0.038 * lw)
    dy = int(0.0325 * lh)
    col_offset = int(0.170 * lw)
    EXTRA_GAP = int(0.032 * lh)  # Add vertical spacing after 10th row

    # Calculate bubble centers
    bubble_centers = []
    for col in range(NUM_COLS):
        x_offset = start_x + col * col_offset
        for row in range(NUM_ROWS):
            # Add spacing for rows after 10
            y_gap = EXTRA_GAP if row >= 10 else 0
            y = start_y + row * dy + y_gap
            centers = []
            for choice in range(NUM_CHOICES):
                x = x_offset + choice * dx
                centers.append((int(x), int(y)))
            bubble_centers.append(centers)

    # Image preprocessing
    gray = cv2.cvtColor(lower_part, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

    selected_answers = []
    multiple_marked = []
    blank_questions = []
    incorrect_questions = []
    score = 0

    for q in range(NUM_ROWS * NUM_COLS):
        fills = []
        for c in range(NUM_CHOICES):
            cx, cy = bubble_centers[q][c]
            roi = thresh[cy - BUBBLE_RADIUS:cy + BUBBLE_RADIUS, cx - BUBBLE_RADIUS:cx + BUBBLE_RADIUS]
            fill = np.sum(roi) // 255
            fills.append(fill)

        valid_choices = [(i, f) for i, f in enumerate(fills) if f >= MIN_FILL]

        if len(valid_choices) == 0:
            selected_answers.append(None)
            blank_questions.append(q + 1)
        elif len(valid_choices) == 1:
            selected_idx = valid_choices[0][0]
            selected_answers.append(selected_idx)
            correct = ANSWER_KEY.get(q)
            if correct is not None and selected_idx == correct:
                score += 1
            else:
                incorrect_questions.append(q + 1)
        else:
            marked_choices = [i for i, _ in valid_choices]
            selected_answers.append(marked_choices)
            multiple_marked.append(q + 1)
            incorrect_questions.append(q + 1)

    # Draw bubbles for debug image
    debug_img = lower_part.copy()
    for q, centers in enumerate(bubble_centers):
        answer = selected_answers[q]
        for c, (cx, cy) in enumerate(centers):
            color = (255, 0, 0)  # Blue default
            thickness = 2
            if answer is None:
                pass
            elif isinstance(answer, list):
                if c in answer:
                    color = (0, 0, 255)  # Red for multiple
                    thickness = 3
            else:
                correct = ANSWER_KEY.get(q)
                if c == answer:
                    color = (0, 255, 0) if correct == c else (0, 165, 255)  # Green if correct, orange if wrong
            cv2.circle(debug_img, (cx, cy), BUBBLE_RADIUS, color, thickness)

    debug_path = "bubble_centers_debug.jpg"
    cv2.imwrite(debug_path, debug_img)

    return {
        "score": score,
        "total_questions": len(ANSWER_KEY),
        "multiple_marked_questions": multiple_marked,
        "blank_questions": blank_questions,
        "skipped_questions": blank_questions,
        "skipped_count": len(blank_questions),
        "incorrect_questions": incorrect_questions,
        "incorrect_count": len(incorrect_questions),
        "selected_answers": selected_answers,
        "debug_image": debug_path
    }

def main():
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python process_answer_sheet.py <image_path>"}))
        sys.exit(1)
    image_path = sys.argv[1]
    result = process_answer_sheet(image_path)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
