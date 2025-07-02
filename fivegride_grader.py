import cv2
import numpy as np
import sys
import json

ANSWER_KEY = {
    0: 3, 1: 2, 2: 1, 3: 1, 4: 1, 5: 2, 6: 3, 7: 0, 8: 2, 9: 3,
    10: 3, 11: 1, 12: 2, 13: 1, 14: 3, 15: 2, 16: 2, 17: 0, 18: 1, 19: 2,
    20: 3, 21: 0, 22: 0, 23: 2, 24: 1, 25: 3, 26: 2, 27: 0, 28: 2, 29: 1,
    30: 1, 31: 2, 32: 0, 33: 1, 34: 0, 35: 3, 36: 2, 37: 1, 38: 2, 39: 0,
    40: 1, 41: 2, 42: 3, 43: 1, 44: 1, 45: 2, 46: 2, 47: 3, 48: 0, 49: 1,
    50: 2, 51: 0, 52: 2, 53: 3, 54: 0, 55: 1, 56: 2, 57: 2, 58: 1, 59: 0,
    60: 3, 61: 2, 62: 1, 63: 0, 64: 2, 65: 2, 66: 1, 67: 3, 68: 1, 69: 0,
    70: 2, 71: 2, 72: 3, 73: 0, 74: 1, 75: 1, 76: 2, 77: 3, 78: 2, 79: 0,
    80: 3, 81: 2, 82: 1, 83: 0, 84: 2, 85: 3, 86: 0, 87: 1, 88: 2, 89: 3,
    90: 0, 91: 2, 92: 1, 93: 2, 94: 0, 95: 3, 96: 1, 97: 2, 98: 3, 99: 1
}

NUM_ROWS = 20
NUM_COLS = 5
NUM_CHOICES = 4
NUM_QUESTIONS = NUM_ROWS * NUM_COLS
bubble_radius = 11

MIN_FILL = 100    # Minimum fill to consider a bubble marked (tune for your sheet)
MIN_DIFF = 60     # Minimum difference between top two fills to accept as single marked

def main():
    try:
        if len(sys.argv) < 2:
            print(json.dumps({"error": "No image path provided"}))
            sys.exit(1)

        image_path = sys.argv[1]
        image = cv2.imread(image_path)
        if image is None:
            print(json.dumps({"error": "Could not load image"}))
            sys.exit(1)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2)

        start_x, start_y = 125, 100
        dx = 33
        dy = 33
        col_offset = 183

        bubble_centers = []
        for col in range(NUM_COLS):
            x_offset = start_x + col * col_offset
            for row in range(NUM_ROWS):
                row_centers = []
                y = start_y + row * dy
                for c in range(NUM_CHOICES):
                    x = x_offset + c * dx
                    row_centers.append((x, y))
                bubble_centers.append(row_centers)

        score = 0
        selected_answers = []
        multiple_marked = []
        blank_questions = []
        details = []

        for q in range(NUM_QUESTIONS):
            fills = []
            for c in range(NUM_CHOICES):
                cx, cy = bubble_centers[q][c]
                roi = thresh[cy-bubble_radius:cy+bubble_radius, cx-bubble_radius:cx+bubble_radius]
                fill = np.sum(roi) // 255
                fills.append(fill)

            max_idx = int(np.argmax(fills))
            sorted_fills = sorted(fills, reverse=True)
            # Check for blank
            if sorted_fills[0] < MIN_FILL:
                status = "Blank"
                selected_answers.append(None)
                blank_questions.append(q+1)
            # Check for multiple marked (if second highest is close to highest)
            elif sorted_fills[0] - sorted_fills[1] < MIN_DIFF:
                status = "Multiple marked"
                marked = [i for i, f in enumerate(fills) if f >= sorted_fills[1]]
                selected_answers.append(marked)
                multiple_marked.append(q+1)
            else:
                status = f"Marked {chr(65+max_idx)}"
                selected_answers.append(max_idx)
            correct = ANSWER_KEY.get(q, None)
            if correct is not None:
                if status.startswith("Marked") and max_idx == correct:
                    score += 1
                    result = "✓"
                else:
                    result = "✗"
                details.append(f"Q{q+1:03d}: {status}, Correct {chr(65+correct)} {result}")
            else:
                details.append(f"Q{q+1:03d}: {status}, Correct N/A")

        response = {
            "score": score,
            "total": len(ANSWER_KEY),
            "multiple_marked": multiple_marked,
            "blank_questions": blank_questions,
        }
        print(json.dumps(response))
    except Exception as e:
        print(json.dumps({"error": "Failed to process image", "details": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
