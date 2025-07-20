import sys
import json
import cv2
import numpy as np

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

NUM_ROWS = 10
NUM_COLS = 5
NUM_CHOICES = 4
BUBBLE_RADIUS = 11

def process_answer_sheet(image_path):
    image = cv2.imread(image_path)
    if image is None:
        return {"error": f"Could not load image at path {image_path}"}

    # Resize image
    RESIZE_WIDTH = 1000
    h0, w0 = image.shape[:2]
    aspect_ratio = h0 / w0
    resized_height = int(RESIZE_WIDTH * aspect_ratio)
    image_resized = cv2.resize(image, (RESIZE_WIDTH, resized_height))
    h, w = image_resized.shape[:2]

    # Crop lower part, adjust fraction to better include first row
    lower_frac = 0.55  # reduced from 0.60 to include more top area
    lower_part = image_resized[int(h * lower_frac):, :]
    lh, lw = lower_part.shape[:2]

    # Bubble centers calculation
    start_x = int(0.115 * lw)
    start_y = int(0.12 * lh)
    dx = int(0.0389 * lw)
    dy = int(0.069 * lh)
    col_offset = int(0.167 * lw)

    bubble_centers = []
    for col in range(NUM_COLS):
        x_offset = start_x + col * col_offset
        for row in range(NUM_ROWS):
            y = start_y + row * dy
            centers = []
            for choice in range(NUM_CHOICES):
                x = x_offset + choice * dx
                centers.append((int(x), int(y)))
            bubble_centers.append(centers)

    # Threshold to find filled bubbles
    gray = cv2.cvtColor(lower_part, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

    MIN_FILL = 100
    MIN_DIFF = 60

    selected_answers = []
    multiple_marked = []
    blank_questions = []
    score = 0

    for q in range(NUM_ROWS * NUM_COLS):
        fills = []
        for c in range(NUM_CHOICES):
            cx, cy = bubble_centers[q][c]
            roi = thresh[cy - BUBBLE_RADIUS:cy + BUBBLE_RADIUS, cx - BUBBLE_RADIUS:cx + BUBBLE_RADIUS]
            fill = np.sum(roi) // 255
            fills.append(fill)

        max_fill = max(fills)
        max_idx = fills.index(max_fill)
        sorted_fills = sorted(fills, reverse=True)

        if max_fill < MIN_FILL:
            selected_answers.append(None)
            blank_questions.append(q + 1)
        elif sorted_fills[0] - sorted_fills[1] < MIN_DIFF:
            marked_choices = [i for i, f in enumerate(fills) if f >= sorted_fills[1]]
            selected_answers.append(marked_choices)
            multiple_marked.append(q + 1)
        else:
            selected_answers.append(max_idx)
            correct = ANSWER_KEY.get(q)
            if correct is not None and max_idx == correct:
                score += 1

    # Draw debug circles with colors:
    # Green: correct, Orange: wrong single, Red: multiple marked, Blue: unmarked
    debug_img = lower_part.copy()
    for q, centers in enumerate(bubble_centers):
        answer = selected_answers[q]
        for c, (cx, cy) in enumerate(centers):
            color = (255, 0, 0)  # Blue default
            thickness = 2
            if answer is None:
                pass  # blue circles
            elif isinstance(answer, list):
                if c in answer:
                    color = (0, 0, 255)  # red multiple
                    thickness = 3
            else:
                correct = ANSWER_KEY.get(q)
                if c == answer:
                    if correct == c:
                        color = (0, 255, 0)  # green correct
                    else:
                        color = (0, 165, 255)  # orange wrong
            cv2.circle(debug_img, (cx, cy), BUBBLE_RADIUS, color, thickness)

    debug_path = "bubble_centers_debug.jpg"
    cv2.imwrite(debug_path, debug_img)

    return {
        "score": score,
        "total_questions": len(ANSWER_KEY),
        "multiple_marked_questions": multiple_marked,
        "blank_questions": blank_questions,
        "selected_answers": selected_answers,
        "debug_image": debug_path
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
