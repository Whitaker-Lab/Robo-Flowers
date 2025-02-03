import cv2
import imutils
import datetime
import os
import numpy as np

cap = cv2.VideoCapture(0)
fps = cap.get(cv2.CAP_PROP_FPS)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
last_mean = 0
detected_motion = False
frame_rec_count = 0
dirName = ""
now = datetime.datetime.now()
date = now.strftime("%Y-%m-%d_%H:%M:%S") + f".{now.microsecond:06d}"
dirFlag = True
print("Start")
while(True):
    ret, frame = cap.read()
    if not ret:
        print("Frame not captured")
        continue
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    result = np.abs(np.mean(gray) - last_mean)
    last_mean = np.mean(gray)
    #print(result)
    if result > .7 and result < 30.0: 
        #print("Motion detected!")
        detected_motion = True
        if dirFlag == True:
            now = datetime.datetime.now()
            dirName = f"{now}"
            if not os.path.exists("BeeImages"):
                os.mkdir("BeeImages")
            dirLoc = f"BeeImages/{dirName}"
            os.mkdir(dirLoc)
            dirFlag = False   
    if detected_motion == True:
        saveLoc = f"BeeImages/{dirName}/Image_{frame_rec_count}.png"
        cv2.imwrite(saveLoc, frame)
        frame_rec_count = frame_rec_count + 1
        #print(frame_rec_count)
    if frame_rec_count == 50:
        #print("Recording Complete")
        cap.release()
        cap = cv2.VideoCapture(0)
        frame_rec_count = 0
        detected_motion = False
        dirFlag = True


    
