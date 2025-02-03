import time
import socket
import sys
import RPi.GPIO as GPIO
import csv
import os
import logging

# Constants
BEAM_PIN = 17
ID = socket.gethostname()  # Use the actual hostname of the Raspberry Pi
current_date = time.strftime("%Y-%m-%d", time.localtime())
CSV_FILE = f"{current_date}_{ID}_data.csv"


# Initialize start_time globally
start_time = None

# Ensure the CSV file exists and has the correct header
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["hostname", "date", "start_time", "end_time", "time_elapsed"])

# Setup logging
log_filename = f"{ID}_{current_date}_IR.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)

def break_beam_callback(channel):
    global start_time  # Declare start_time as global
    if GPIO.input(BEAM_PIN):
        logging.info("Bee Left")
        print("Bee Left")
        if start_time is not None:  # Check if start_time has been initialized
            end_time = time.time()
            elapsed_time = end_time - start_time
            save_data(start_time, end_time, elapsed_time)
            start_time = None  # Reset start_time after saving data
        else:
            logging.info("Timer has not started yet.")
    else:
        logging.info("Bee Detected")
        print("Bee Detected")
        start_time = time.time()  # Update start_time

def save_data(start, end, elapsed):
    date = time.strftime("%Y-%m-%d", time.localtime(start))
    start_str = time.strftime("%H:%M:%S", time.localtime(start))
    end_str = time.strftime("%H:%M:%S", time.localtime(end))
    
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([ID, date, start_str, end_str, elapsed])
        logging.info(f"Data saved: {ID}, {date}, {start_str}, {end_str}, {elapsed}")

GPIO.setmode(GPIO.BCM)
GPIO.setup(BEAM_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BEAM_PIN, GPIO.BOTH, callback=break_beam_callback)
logging.info("System ready. Press Ctrl+C to exit.")
try:
    while True:
        time.sleep(1)  # Keep the program running
except KeyboardInterrupt:
    logging.info("Program terminated by user.")
finally:
    GPIO.cleanup()
