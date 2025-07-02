import cv2
import numpy as np
import imutils
from imutils import contours
import four_point   # make sure the helper is in the same folder

# ────────────────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────────────────
ANSWER_KEY = {0: 1, 1: 4, 2: 0, 3: 2, 4: 1}   # q‑index → choice index

# ────────────────────────────────────────────────────────────
# LOAD + LOCATE SHEET
# ────────────────────────────────────────────────────────────
image = cv2.imread("omr.png")
if image is None:
    raise FileNotFoundError("Couldn’t load 'omr.png' – check the path.")

gray     = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred  = cv2.GaussianBlur(gray, (5, 5), 0)
edged    = cv2.Canny(blurred, 75, 200)

cnts = imutils.grab_contours(
    cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
)

docCnt = None
for c in sorted(cnts, key=cv2.contourArea, reverse=True):
    peri   = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    if len(approx) == 4:          # sheet = biggest 4‑corner contour
        docCnt = approx
        break
if docCnt is None:
    raise RuntimeError("OMR sheet contour not found.")

paper  = four_point.four_point_transform(image, docCnt.reshape(4, 2))
warped = four_point.four_point_transform(gray,  docCnt.reshape(4, 2))

# ────────────────────────────────────────────────────────────
# THRESHOLD + BUBBLE DETECTION
# ────────────────────────────────────────────────────────────
_, thresh = cv2.threshold(          # NB: unpack second return value only
    warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
)

cnts = imutils.grab_contours(
    cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
)

questionCnts = []
for c in cnts:
    x, y, w, h = cv2.boundingRect(c)
    aspect     = w / float(h)
    if w >= 20 and h >= 20 and 0.9 <= aspect <= 1.1:   # roughly square
        questionCnts.append(c)

questionCnts = contours.sort_contours(questionCnts,
                                      method="top-to-bottom")[0]

# ────────────────────────────────────────────────────────────
# GRADE
# ────────────────────────────────────────────────────────────
correct = 0
for q, i in enumerate(np.arange(0, len(questionCnts), 5)):   # 5 bubbles/q
    bubbleCnts = contours.sort_contours(questionCnts[i:i + 5])[0]
    bubbled    = None

    for j, c in enumerate(bubbleCnts):
        mask = np.zeros(thresh.shape, dtype="uint8")
        cv2.drawContours(mask, [c], -1, 255, -1)
        total = cv2.countNonZero(cv2.bitwise_and(thresh, thresh, mask=mask))

        if bubbled is None or total > bubbled[0]:
            bubbled = (total, j)        # (pixel count, index)

    if ANSWER_KEY.get(q) == bubbled[1]:
        correct += 1

print(f"Score: {correct}/{len(ANSWER_KEY)}")
