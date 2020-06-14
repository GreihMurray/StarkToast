
import cv2
import numpy as np
import math
import sys
from colour import Color, hex2rgb
import tkinter
from tkinter import filedialog
import time

from vpython import *

angles = [0]

fHold = [0]

red = Color("red")
blue = Color("blue")

colors = list(red.range_to(blue, 200))

rads = 100

holdF = 0
rads = 0

inc = 0

for colorNow in colors:
    colorNow = str(colorNow.hex_l)
    print('tttt', colorNow)
    colorNow = hex2rgb(colorNow)
    print(colorNow)
    colors[inc] = colorNow
    inc = inc + 1

print()
scene.forward = vector(-0.4,-0.3,-1)
scene.ambient = color.gray(0.2)

front = box(pos=vector(0,0,6), size=vector(12,12,12), color=color.white, shininess=0.3)

def Save(save):
    root = tkinter.Tk()
    root.withdraw()

    radians = "radians: " + str(rads) + '\n'
    xVal = "X Value: " + str(front.size.x) + '\n'
    yVal = "Y Value: " + str(front.size.y) + '\n'
    zVal = "Z Value: " + str(front.size.z) + '\n'
    color = front.color
    color = str(color).strip('<,>')
    color = "Color (RGB, scale 255 to 1): " + str(color) + '\n'

    filePath = filedialog.asksaveasfilename(parent=root, defaultextension=".txt", initialdir='/Documents', initialfile='newSave.txt')

    file = open(filePath, 'w')

    file.write(radians)
    file.write(xVal)
    file.write(yVal)
    file.write(zVal)
    file.write(color)

    file.close()

scene.append_to_caption("\n")


def Angle(angleNow):
    #print(angleNow.value * 10)

    oldRange = 10
    newRange = 2*pi

    newValue = (((angleNow.value * 10) * newRange)/oldRange) + 0

    angles.append(newValue)

    if angles[1] > angles[0]:
        newValue = -((2 * pi) - newValue)
    else:
        newValue = (2*pi) - newValue

    front.rotate(angle=radians(newValue))

    angles.pop(0)


def Load(load):
    root = tkinter.Tk()
    root.withdraw()

    filePath = filedialog.askopenfilename(parent=root, initialdir='/Documents', initialfile='tmp',
                           filetypes=[("All files", "*")])

    file = open(filePath, 'r')

    text = file.read()

    file.close()

    lines = text.split('\n')

    lines.pop()

    infoList = []

    for line in lines:
        info = line.split(':')
        infoList.append(info[1])

    colorVals = infoList[4].split(',')

    for element in colorVals:
        element = element.strip()

    print(colorVals)

    front.rotate(angle=radians(float(infoList[0])))
    front.size.x = float(infoList[1])
    front.size.y = float(infoList[2])
    front.size.z = float(infoList[3])
    front.color = vector(float(colorVals[0]), float(colorVals[1]), float(colorVals[2]))

def Red(red):
    color = str(front.color).strip('<>')
    hold, green, blueIn = color.split(', ')

    front.color = vector(red.value, float(green), float(blueIn))

def Green(green):
    color = str(front.color).strip('<>')
    red, hold, blueIn = color.split(', ')

    front.color = vector(float(red), green.value, float(blueIn))

def Blue(blue):
    color = str(front.color).strip('<>')
    red, green, hold = color.split(', ')

    front.color = vector(float(red), float(green), blue.value)

def Xvalue(x):
    oldRange = 1
    newRange = 250

    newValue = ((float(x.value) * newRange) / oldRange) + 5

    front.size.x = newValue

def Yvalue(y):
    oldRange = 1
    newRange = 250

    newValue = ((float(y.value) * newRange) / oldRange) + 5

    front.size.y = newValue

def Zvalue(z):
    oldRange = 1
    newRange = 250

    newValue = ((float(z.value) * newRange) / oldRange) + 5

    front.size.z = newValue

button(bind=Save, text="Save Configuration")

scene.append_to_caption("\t\t\tAlter Angle\n\n")

button(bind=Load, text="Load Configuration")

scene.append_to_caption('\t\t')

slider(bind=Angle, text="Angle")

scene.append_to_caption('\n\nRed\t\t')

scene.append_to_caption("\t\t\t\t\t\t\t\tX Value\n\n")

slider(bind=Red)

slider(bind=Xvalue)

scene.append_to_caption('\n\nGreen\t\t')

scene.append_to_caption('\t\t\t\t\t\t\t\tY Value\n\n')

slider(bind=Green)

slider(bind=Yvalue)

scene.append_to_caption('\n\nBlue\t\t')

scene.append_to_caption(('\t\t\t\t\t\t\t\tZ Value\n\n'))

slider(bind=Blue)

slider(bind=Zvalue)

cap = cv2.VideoCapture(0)


while (1):
    try:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        kernel = np.ones((3, 3), np.uint8)

        roi = frame[100:300, 100:300]

        cv2.rectangle(frame, (100, 100), (300, 300), (0, 255, 255), 2)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        cv2.putText(frame, "Place hand in box", (100, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 4)
        cv2.putText(frame, "Place hand in box", (100, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)


        # # define range of skin color in HSV
        lower_skin = np.array([5, 80, 80], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)

        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        mask = cv2.dilate(mask, kernel, iterations=4)

        mask = cv2.GaussianBlur(mask, (5, 5), 100)

        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        cnt = max(contours, key=lambda x: cv2.contourArea(x))

        epsilon = 0.0005 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        hull = cv2.convexHull(cnt)

        areahull = cv2.contourArea(hull)
        areacnt = cv2.contourArea(cnt)

        arearatio = ((areahull - areacnt) / areacnt) * 100

        hull = cv2.convexHull(approx, returnPoints=False)
        defects = cv2.convexityDefects(approx, hull)

        l = 0

        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(approx[s][0])
            end = tuple(approx[e][0])
            far = tuple(approx[f][0])
            pt = (100, 180)

            fHold.append(f)

            if (fHold[0] - fHold[1]) > 30 or (fHold[0] - fHold[1]) < -20:
                holdF = f
                print('\n\n', (fHold[0] - fHold[1]), '\n\n')
            else:
                holdF = holdF
            fHold.pop(0)

            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            s = (a + b + c) / 2
            ar = math.sqrt(s * (s - a) * (s - b) * (s - c))

            d = (2 * ar) / a

            angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

            if angle <= 90 and d > 30:
                l += 1
                cv2.circle(roi, far, 3, [255, 0, 0], -1)

            cv2.line(roi, start, end, [0, 255, 0], 2)

        l += 1

        font = cv2.FONT_HERSHEY_SIMPLEX
        if l == 1:
            if areacnt < 2000:
                cv2.putText(frame, 'No hand detected', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            else:
                if arearatio < 12:
                    cv2.putText(frame, 'No changes being made', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

                else:
                    cv2.putText(frame, 'Altering Color', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

                    time.sleep(.05)

                    print(holdF)

                    colorVal = colors[holdF]

                    colorVal = str(colorVal).strip("()")

                    holdVals = colorVal.split(', ')

                    redVal = float(holdVals[0])
                    blueVal = float(holdVals[1])
                    greenVal = float(holdVals[2])

                    rate(500)

                    front.color = vector(redVal, greenVal, blueVal)


        #Changes X dimension
        elif l == 2:
            cv2.putText(frame, 'Altering X Value', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            Xchange = (s - 200)


            XcheckSize = Xchange

            newX, NegY = far

            front.size.x = front.size.x + (newX - front.size.x)

        #Changes Y Dimension
        elif l == 3:

            cv2.putText(frame, 'Altering Y Value', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            if e >= 200:
                Ychange = (s - 200)
            else:
                Ychange = (200 - s)

            YcheckSize = Ychange
            NegX, front.size.y = far

        #Changes Z Dimension
        elif l == 4:
            cv2.putText(frame, 'Altering Z Value', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

            if e >= 200:
                Zchange = (s - 200)
            else:
                Zchange = (200 - s)

            ZcheckSize = Zchange
            newZ, NegY = far

            front.size.z = newZ

        elif l == 5:
            cv2.putText(frame, 'Altering Angle', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)
            rads = f
            front.rotate(angle=radians(f/100))
        elif l == 6:
            cv2.putText(frame, 'reposition', (0, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

        else:
            cv2.putText(frame, 'reposition', (10, 50), font, 2, (0, 0, 255), 3, cv2.LINE_AA)

        cv2.imshow('frame', frame)

    except:
        pass

    key = cv2.waitKey(5) & 0xFF
    if key == ord('q'):
        break

cv2.imshow('frame', frame)
cv2.destroyAllWindows()
cap.release()
sys.exit('End of Program')
