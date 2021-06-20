import cv2
import numpy as np

logo = cv2.imread('example.jpg') # jpg / png recomanded
bg = cv2.imread('template.jpg')

height_logo, width_logo = logo.shape[:2]
height_bg, width_bg = bg.shape[:2]
gray_logo = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
logo_recognize_threshold = 200
ret, binary_logo = cv2.threshold(gray_logo, logo_recognize_threshold, 255, cv2.THRESH_TRUNC)
binary_logo = logo_recognize_threshold - binary_logo

min_h = 0
max_h = height_logo
for i in range(height_logo):
    if sum(binary_logo[i]) > 0:
        min_h = i
        break
for i in range(height_logo - 1, 0, -1):
    if sum(binary_logo[i]) > 0:
        max_h = i
        break
binary_logo = np.rot90(binary_logo, -1)
min_v = 0
for i in range(width_logo):
    if sum(binary_logo[i]) > 0:
        min_v = i
        break
radius = (max_h - min_h) // 2
center = (min_v + radius, min_h + radius)
#print(center, radius)

logo_circle = np.zeros((height_logo, width_logo, 1), np.uint8)
logo_circle = cv2.circle(logo_circle, center, radius, (1), -1)
logo_transparent = np.zeros((height_logo, width_logo, 4), np.uint8)
for i in range(3):
    logo_transparent[:, :, i] = np.multiply(logo[:, :, i], logo_circle[:, :, 0])
logo_circle[logo_circle == 1] = 255
logo_transparent[:, :, 3] = logo_circle[:, :, 0]

logo_transparent = logo_transparent[center[1] - radius:center[1] + radius, center[0] - radius:center[0] + radius]

bg_transparent = np.zeros((height_bg, width_bg, 4), np.uint8)
bg_transparent[:, :, 0] = bg[:, :, 0]
bg_transparent[:, :, 1] = bg[:, :, 1]
bg_transparent[:, :, 2] = bg[:, :, 2]
bg_transparent[:, :, 3] = np.zeros((height_bg, width_bg), np.uint8) + 255

def add_logo(bg, logo, target_size, rotation, position):
    logo_scaled = cv2.resize(logo, (target_size, target_size))
    roi = bg[position[0]:position[0]+target_size, position[1]:position[1]+target_size]
    mask = np.zeros((target_size, target_size, 1), np.uint8)
    mask = cv2.circle(mask, (target_size//2, target_size//2), target_size//2, (255), -1)
    mask_inv = cv2.bitwise_not(mask)
    frame_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
    img_fg = cv2.bitwise_and(logo_scaled, logo_scaled, mask=mask)
    M = cv2.getRotationMatrix2D((target_size//2, target_size//2), rotation, 1.0)
    img_fg = cv2.warpAffine(img_fg, M, (target_size, target_size))
    dst = cv2.add(frame_bg, img_fg)
    bg[position[0]:position[0]+target_size, position[1]:position[1]+target_size] = dst
    return bg

result = add_logo(bg_transparent, logo_transparent, 400, 0, (430, 110))
result = add_logo(result, logo_transparent, 120, 39, (1165, 840))

cv2.imwrite('your-roll.jpg', result)
cv2.imshow('result', result)
cv2.waitKey(0)
