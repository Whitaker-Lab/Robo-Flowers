import cv2
import datetime
import os
import numpy as np
import socket  # For getting the Raspberry Pi's hostname

# Get the Raspberry Pi's hostname
pi_name = socket.gethostname()

# Create the main folder for images if it doesn't exist
base_folder = "BeeImages"
if not os.path.exists(base_folder):
    os.mkdir(base_folder)

# Create a subfolder for this particular Raspberry Pi
output_folder = os.path.join(base_folder, pi_name)
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Initialize video capture (device 0) and set resolution
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Initialize variables for motion detection and image saving
last_mean = 0           # Mean brightness of the previous frame
detected_motion = False # Flag to indicate if motion is detected
frame_rec_count = 0     # Counter for saved frames in one motion event

print("Start")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame not captured")
        continue

    # Convert the frame to grayscale for brightness calculation
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    current_mean = np.mean(gray)
    diff = abs(current_mean - last_mean)
    last_mean = current_mean

    # Determine if motion has occurred based on brightness change
    if 0.7 < diff < 30.0:
        detected_motion = True

    # If motion is detected, save the frame with a timestamp as its filename
    if detected_motion:
        now = datetime.datetime.now()
        # Format the timestamp (using '-' instead of ':' avoids filename issues)
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S.%f")
        save_path = os.path.join(output_folder, f"{timestamp}.png")
        cv2.imwrite(save_path, frame)
        frame_rec_count += 1

    # After saving 50 frames, reset for a new motion event
    if frame_rec_count == 50:
        frame_rec_count = 0
        detected_motion = False

    # Optionally, display the video feed so you can see what's happening
    cv2.imshow("Camera Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
