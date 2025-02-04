import cv2  # OpenCV library for computer vision tasks
import imutils  # Utility functions for image processing (not used in this code)
import datetime  # To work with date and time
import os  # To interact with the file system (for creating directories, saving files, etc.)
import numpy as np  # For numerical operations, like calculating means of arrays

# Initialize video capture from the default webcam (device index 0)
cap = cv2.VideoCapture(0)

# Retrieve the frames per second (FPS) of the capture device (though this value isn't used later)
fps = cap.get(cv2.CAP_PROP_FPS)

# Set the resolution of the captured frames to 640x480 pixels
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Initialize variables for motion detection and image saving
last_mean = 0           # Stores the mean brightness of the previous frame
detected_motion = False # Flag to indicate if motion has been detected
frame_rec_count = 0     # Counter for the number of frames saved during a motion event
dirName = ""            # Name of the directory where images will be saved

# Get the current date and time; format it into a string (this one isn't used later)
now = datetime.datetime.now()
date = now.strftime("%Y-%m-%d_%H:%M:%S") + f".{now.microsecond:06d}"

dirFlag = True  # Flag to control creation of a new directory when a new motion event is detected

print("Start")  # Notify that the program has started

# Main loop: continuously capture and process frames from the webcam
while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()

    # If a frame wasn't successfully captured, log the issue and skip to the next loop iteration
    if not ret:
        print("Frame not captured")
        continue

    # Convert the captured frame to grayscale to simplify brightness calculations
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Calculate the absolute difference between the current frame's mean brightness and the previous frame's
    result = np.abs(np.mean(gray) - last_mean)
    
    # Update the last_mean for the next iteration's comparison
    last_mean = np.mean(gray)
    
    # Determine if the brightness change qualifies as motion:
    # - Change greater than 0.7 (to avoid noise)
    # - And less than 30.0 (to ignore extreme changes like sudden light flashes)
    if result > 0.7 and result < 30.0:
        detected_motion = True  # Set the flag indicating that motion is detected
        
        # If this is the first frame of the new motion event, create a directory to store the images
        if dirFlag:
            now = datetime.datetime.now()  # Get the current date and time for naming the directory
            dirName = f"{now}"             # Use the current timestamp as the directory name
            
            # Create the main folder "BeeImages" if it doesn't already exist
            if not os.path.exists("BeeImages"):
                os.mkdir("BeeImages")
            
            # Create a subdirectory within "BeeImages" using the timestamp
            dirLoc = f"BeeImages/{dirName}"
            os.mkdir(dirLoc)
            
            # Reset the flag to prevent creating multiple directories during the same motion event
            dirFlag = False

    # If motion has been detected, save the current frame as an image
    if detected_motion:
        # Define the location and filename for the saved image
        saveLoc = f"BeeImages/{dirName}/Image_{frame_rec_count}.png"
        cv2.imwrite(saveLoc, frame)  # Save the current frame as a PNG file
        
        # Increment the frame counter after saving the image
        frame_rec_count += 1

    # After saving 50 frames, reset the system to be ready for a new motion event
    if frame_rec_count == 50:
        cap.release()  # Release the current capture (helps reset any internal buffers)
        cap = cv2.VideoCapture(0)  # Reinitialize video capture from the webcam
        frame_rec_count = 0  # Reset the frame counter for the next motion event
        detected_motion = False  # Reset the motion detection flag
        dirFlag = True  # Reset the directory creation flag for the next motion event

