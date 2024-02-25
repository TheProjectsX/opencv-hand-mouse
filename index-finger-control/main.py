import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import time
import pyautogui

# Disabling pyautogui Failsafe (Though, not recommended by authors!)
pyautogui.FAILSAFE = False


# Resize the Screen Shot
def resize_with_max_dimensions(image):
    # Get original image dimensions
    original_height, original_width = image.shape[:2]

    # Calculate aspect ratio
    aspect_ratio = original_width / original_height

    # Calculate new dimensions while keeping aspect ratio
    if aspect_ratio > FrameWidth / FrameHeight:
        new_width = FrameWidth
        new_height = int(FrameWidth / aspect_ratio)
    else:
        new_height = FrameHeight
        new_width = int(FrameHeight * aspect_ratio)

    # Resize the image
    resized_image = cv2.resize(image, (new_width, new_height))

    return resized_image


# Get Corresponding axis points of the screen
# def getCorAxis(init_x, init_y, orgSShot):
def getCorAxis(init_x, init_y):
    # height, width, c = orgSShot

    # Getting the index position of the full frame corresponding to Screen Shown
    # scale_x = width / FrameWidth
    # scale_y = height / FrameHeight

    # corr_init_x = init_x * scale_x
    # corr_init_y = init_y * scale_y

    # Getting the mouse position of the full screen corresponding to Screen Shown
    scale_x = ScreenWidth / (FrameWidth)
    scale_y = ScreenHeight / (FrameHeight)

    # corr_x = corr_init_x * scale_x
    # corr_y = corr_init_y * scale_y
    corr_x = init_x * scale_x
    corr_y = init_y * scale_y

    return corr_x, corr_y


# Global & Const Variables
# Video Frame Width and Height
FrameWidth, FrameHeight = 640, 360
FramePaddingX, FramePaddingY = None, None
paddingAmount = 0.2  # 20%
# Main Screen Width and Height
ScreenWidth, ScreenHeight = pyautogui.size()

# Initializing Hand Tracker
detector = HandDetector(maxHands=1, detectionCon=0.6)

# Setting the Finger Tips axis
xi, yi = None, None  # Index
xp, yp = None, None  # Pinky

# Video Capture
cap_vid = cv2.VideoCapture(1)
cap_vid.set(cv2.CAP_PROP_FRAME_WIDTH, FrameWidth)
cap_vid.set(cv2.CAP_PROP_FRAME_HEIGHT, FrameHeight)
windowName = "Hand Moved Mouse"

mouseDown = False
lastScreenShot = 0
blankScreen = np.zeros((FrameHeight, FrameWidth, 3), dtype=np.uint8)
while cap_vid.isOpened():
    ret, frame = cap_vid.read()
    if not ret:
        continue

    if ((time.time() - lastScreenShot) > 0.1):
        sShotFull = np.array(pyautogui.screenshot())
        # Resize to Frame W,H corresponding
        # dimRes = resize_with_max_dimensions(sShotFull)
        # if (FramePaddingX is None):
        #     FramePaddingX = int(dimRes.shape[1] * paddingAmount)
        #     FramePaddingY = int(dimRes.shape[0] * paddingAmount)
        # # Reduce the Size to 20%
        # sShotFull = cv2.resize(
        #     sShotFull, (dimRes.shape[1]-(FramePaddingX*2), dimRes.shape[0]-(FramePaddingY*2)))
        sShotFull = cv2.resize(
            sShotFull, (FrameWidth, FrameHeight))
        # sShot = cv2.resize(
        #     sShot, (FrameWidth, FrameHeight))
        sShotFull = cv2.cvtColor(sShotFull, cv2.COLOR_RGB2BGR)
        # tmp = blankScreen.copy()
        # tmp[FramePaddingY:sShotFull.shape[0] + FramePaddingY,
        #     FramePaddingX:sShotFull.shape[1] + FramePaddingX, :] = sShotFull
        # sShot = tmp.copy()
        sShot = sShotFull
        lastScreenShot = time.time()

    img = cv2.flip(frame, cv2.CAP_PROP_XI_DECIMATION_HORIZONTAL)
    # draw=True if Hand Needs to be drawn
    hands, _ = detector.findHands(img, flipType=False, draw=True)
    if not (len(hands) == 0):
        fingersUp = detector.fingersUp(hands[0])
        if (fingersUp[1] == 1):  # If the index finger is Up
            lmList = hands[0]["lmList"]
            xi, yi, c = lmList[8]  # 8 is the Index finger tip
            # if (FramePaddingX < xi < FramePaddingX+sShotFull.shape[1]) and (FramePaddingY < yi < FramePaddingY+sShotFull.shape[0]):
            if (fingersUp[4] == 1):  # If the Pinky finger is also up, then click happens!
                xp, yp, c = lmList[20]
                if not mouseDown:
                    mouseDown = True
                    pyautogui.mouseDown()
            else:  # if not up, then unclicks....
                if (mouseDown):
                    mouseDown = False
                    pyautogui.mouseUp()
                    xp, yp, c = None, None, None

            corr_x, corr_y = getCorAxis(xi, yi)
            pyautogui.moveTo(corr_x, corr_y)
            # Via this line (& CODE:1), cap_vid frame will be shown CODE:1
            # img = cv2.circle(img, (x, y), 4, (255, 0, 255), -1)
            # Via this line (& CODE:2), Only the Screen will be shown CODE:2
            # img = cv2.circle(sShot, (x, y), 4, (255, 0, 255), -1)
        # else:
        #     xi, yi, c = None, None, None

    for hand in hands:
        fingers = detector.fingersUp(hand)
        if (fingers[1] != 1):
            continue

        lmList = hand["lmList"]
        idxPos = lmList[8]

    # Via this line (& CODE:1), cap_vid frame will be shown CODE:1
    img = cv2.addWeighted(img, 0.2, sShot, 0.8, 0)
    # Via this line (& CODE:2), Only the Screen will be shown CODE:2
    # img = cv2.addWeighted(sShot, 0.5, sShot, 0.5, 0)

    # Adding finger tips :: Adding it down For it to be clear as the sky!
    if (xi is not None):
        # Index finger tip
        img = cv2.circle(img, (xi, yi), 4, (255, 0, 255), -1)

    if (xp is not None):
        img = cv2.circle(img, (xp, yp), 4, (0, 255, 0), -1)  # Pinky finger tip

    cv2.imshow(windowName, img)
    if (cv2.waitKey(1) & 0xFF == 27):
        break
    if (cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) < 1):
        break


# Release Camera
cap_vid.release()
cv2.destroyAllWindows()
