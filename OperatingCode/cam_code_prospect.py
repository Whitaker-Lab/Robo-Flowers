import cv2
import datetime
import os
import numpy as np
import socket  # For getting the Raspberry Pi's hostname
import time

# Get the Raspberry Pi's hostname
pi_name = socket.gethostname()

# Base folder for all images
base_folder = "BeeImages"
if not os.path.exists(base_folder):
    os.mkdir(base_folder)

# Get today's date to create a dated subfolder
today_date = datetime.datetime.now().strftime("%Y-%m-%d")
output_folder = os.path.join(base_folder, f"{today_date}_{pi_name}")

# Create the directory for today's images if it doesn't exist
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Initialize video capture (device 0) and set resolution
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Motion detection parameters
last_mean = 0  # Mean brightness of the previous frame
detected_motion = False
last_capture_time = time.time()  # Timestamp of last saved image
cooldown_time = 2  # Time (in seconds) between saved images

print("Start")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame not captured")
        continue

    # Convert to grayscale for motion detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    current_mean = np.mean(gray)
    diff = abs(current_mean - last_mean)
    last_mean = current_mean

    # Detect motion based on brightness change
    if 0.7 < diff < 30.0:
        detected_motion = True

    # If motion is detected and cooldown has passed, save the image
    if detected_motion and (time.time() - last_capture_time) > cooldown_time:
        now = datetime.datetime.now()
        time_stamp = now.strftime("%H-%M-%S")  # Only time in filename
        save_path = os.path.join(output_folder, f"{time_stamp}.png")
        cv2.imwrite(save_path, frame)
        print(f"Saved image: {save_path}")
        last_capture_time = time.time()  # Update last capture time
        detected_motion = False  # Reset motion detection after saving

    # Show live feed (optional)
    cv2.imshow("Camera Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

