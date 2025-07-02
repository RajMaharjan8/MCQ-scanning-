import cv2
import numpy as np

def find_sheet_contour(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edged = cv2.Canny(blur, 50, 200)
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4:
            return np.float32([point[0] for point in approx])
    return None

def order_points(pts):
    # Orders points as: top-left, top-right, bottom-right, bottom-left
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def warp_sheet(image, corners, width=1000, height=1500):
    rect = order_points(corners)
    dst = np.array([
        [0, 0],
        [width-1, 0],
        [width-1, height-1],
        [0, height-1]
    ], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (width, height))
    return warped

# --- MAIN SCRIPT ---
image = cv2.imread('new.png')
corners = find_sheet_contour(image)
if corners is None:
    print("Could not find sheet corners. Make sure the whole sheet is visible and has a clear border.")
    exit()

# Set these to your standard sheet size in pixels
WARP_WIDTH = 1000
WARP_HEIGHT = 1500

warped = warp_sheet(image, corners, width=WARP_WIDTH, height=WARP_HEIGHT)
cv2.imwrite('aligned_new.png', warped)
print("Sheet aligned and saved as aligned_new.png")

# Now run your bubble detection code on 'aligned_new.png'!
