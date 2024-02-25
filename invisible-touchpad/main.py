import cv2
from cvzone.HandTrackingModule import HandDetector
import pyautogui

# Disabling pyautogui Failsafe (Though, not recommended by authors!)
pyautogui.FAILSAFE = False


# Perform Movement Operation
def performMovement(hands):
    global mouseDown, dblClickOpen, lastIdxX, lastIdxY

    if (len(hands) == 0):
        if (mouseDown):
            mouseDown = False
            pyautogui.mouseUp()
        return

    fingersUp = detector.fingersUp(hands[0])
    # If the index finger is Up
    if (fingersUp[2] == 1 and fingersUp[3] == 1):
        if (lastIdxX is not None):
            lastIdxX, lastIdxY = None, None
        if not (dblClickOpen):
            dblClickOpen = True
        if (mouseDown):
            mouseDown = False
            pyautogui.mouseUp()

        return

    if (fingersUp[1] == 1):
        lmList = hands[0]["lmList"]
        xi, yi, c = lmList[8]  # 8 is the Index finger tip
        # If the Pinky finger (only) is also up, then click happens!
        if ((fingersUp[4] == 1)):
            if not mouseDown:
                mouseDown = True
                pyautogui.mouseDown()
        else:  # if not up, then un-clicks....
            if (mouseDown):
                mouseDown = False
                pyautogui.mouseUp()

        # If we don't want to Move the cursor while Clicking, we can return from here
        # Though click + movement is not a good Combination, But we can use this to resize any window
        if (mouseDown):
            lastIdxX, lastIdxY = None, None
            return

        if (lastIdxX is None):
            lastIdxX = xi
            lastIdxY = yi

            return

        """
        # Original algorithm says to Subtract xi/yi from lastIdxX/Y
        diffX = lastIdxX - xi
        diffY = lastIdxY - yi
        """

        # But as we are flipping the image horizontally, we need to do the opposite. Cause? Think it as, the Video shown is the mirror image of original
        # In reality, we will not show the camera feed. in that case, we will not need to flip the image, and we can use the original algorithm
        diffX = xi - lastIdxX
        diffY = yi - lastIdxY
        # Doubling the value for faster movement
        diffX *= movementBoost
        diffY *= movementBoost

        """
        # Option 01: Add the moved Axis's with the current mouse position and then, move mouse to that axis relative to the Screen ("moveto" function)
        mouseNowX, mouseNowY = pyautogui.position()
        mouseNewX = mouseNowX + diffX
        mouseNewY = mouseNowY + diffY
        pyautogui.moveTo(mouseNewX, mouseNewY)
        """

        # Option 02: Move the mouse relative to it's current position ("move" function)
        pyautogui.move(diffX, diffY)
        lastIdxX = xi
        lastIdxY = yi
    # If only pinky finger is up, we will perform double click
    elif (fingersUp[4] == 1):
        if (dblClickOpen):
            dblClickOpen = False
            pyautogui.doubleClick()
    else:
        if (lastIdxX is not None):
            lastIdxX, lastIdxY = None, None


# Global & Const Variables
# Video Frame Width and Height
FrameWidth, FrameHeight = 960, 540

# Main Screen Width and Height
ScreenWidth, ScreenHeight = pyautogui.size()

# Setting the Finger Tips axis
xi, yi = None, None  # Index

# How much speed is increased for mouse movement
movementBoost = 1.5

# Initializing Hand Tracker
detector = HandDetector(maxHands=1, detectionCon=0.7)

# Video Capture
cap_vid = cv2.VideoCapture(1)
cap_vid.set(cv2.CAP_PROP_FRAME_WIDTH, FrameWidth)
cap_vid.set(cv2.CAP_PROP_FRAME_HEIGHT, FrameHeight)
windowName = "Invisible Touch Pad"

mouseDown = False
dblClickOpen = True
lastIdxX, lastIdxY = None, None

print("\nCursor movement is in your Hand now!")
while cap_vid.isOpened():
    try:
        ret, frame = cap_vid.read()
        if not ret:
            continue

        # draw=True if Hand Needs to be drawn
        img = cv2.flip(frame, cv2.CAP_PROP_XI_DECIMATION_HORIZONTAL)
        hands, _ = detector.findHands(img, flipType=False, draw=True)

        """
        # Without Flipping the image (When will not show the video feed)
        img = cv2.flip(frame, cv2.CAP_PROP_XI_DECIMATION_HORIZONTAL)
        hands, _ = detector.findHands(img, flipType=False, draw=True)
        """
        performMovement(hands)

        # Usually, we will not show the Video Feed
        # cv2.imshow(windowName, img)
        if (cv2.waitKey(1) & 0xFF == 27):
            break

        # We will remove below condition if we are not showing the video feed from the start. But if we show the video feed, below condition is important
        # if (cv2.getWindowProperty(windowName, cv2.WND_PROP_VISIBLE) < 1):
        #     break
    except:
        break

print("\nCursor movement is back to the Mouse!")
# Release Camera
cap_vid.release()
cv2.destroyAllWindows()
