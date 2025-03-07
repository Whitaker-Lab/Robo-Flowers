import sys
import time
from datetime import datetime
import subprocess
import logging
import os
import RPi.GPIO as GPIO  # Only needed if you're using local GPIO testing

def check_online(hostname):
    """
    Check if a device is online by pinging it.
    """
    try:
        output = subprocess.check_output(
            ['ping', '-c', '1', hostname],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        if "1 received" in output:
            logging.info(f"{hostname} is online.")
            return True
        else:
            logging.error(f"{hostname} is offline.")
            return False
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to ping {hostname}: {e.output}")
        return False

def check_cameras(pi_num):
    """
    Check if a USB camera is connected to a remote device.
    """
    hostname = f"pi{pi_num}.wifi.etsu.edu"  
    username = f"pi{pi_num}"
    try:
        lsusb_cmd = f"ssh {username}@{hostname} lsusb"  
        usb_output = subprocess.check_output(
            lsusb_cmd, shell=True,
            stderr=subprocess.STDOUT, 
            universal_newlines=True
        )
        # Look for keywords that indicate a USB camera in the lsusb output.
        has_camera = any(keyword in usb_output.lower() for keyword in ["camera", "pixel"])
        if has_camera:
            logging.info(f"{hostname} has a USB camera connected.")
        else:
            logging.warning(f"No USB camera detected on {hostname}.")
        return has_camera
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to check USB devices on {hostname}: {e.output}")
        return False

def check_ir_sensor(pi_num):
    """
    Check if the IR sensor is functioning on the remote device.
    This function SSH's into the Pi and runs a remote test script that simulates
    an IR beam break and verifies sensor output.
    
    It expects the remote test script to output a known success message, e.g. 'IR sensor OK'.
    """
    hostname = f"pi{pi_num}.wifi.etsu.edu"
    username = f"pi{pi_num}"
    # Adjust the path below to point to your remote test script.
    test_command = "python3 /home/pi/test_ir_sensor.py"
    
    try:
        result = subprocess.check_output(
            ["ssh", f"{username}@{hostname}", test_command],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            timeout=10  # Prevent hanging indefinitely
        )
        if "IR sensor OK" in result:
            logging.info(f"IR sensor on {hostname} is functioning correctly.")
            return True
        else:
            logging.warning(f"IR sensor test on {hostname} did not return expected result.")
            return False
    except subprocess.CalledProcessError as e:
        logging.error(f"IR sensor test failed on {hostname}: {e.output}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during IR sensor test on {hostname}: {e}")
        return False

if __name__ == "__main__":
    # Define hostnames for your Pis.
    pi_hosts = [f"pi{i}.wifi.etsu.edu" for i in range(1, 21)]
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H%M%S")

    # Create directories if they don't exist.
    local_directory = "/home/rpimain/Data"
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    log_directory = "rollCall_logFiles"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_filename = f"{log_directory}/{current_date}_{current_time}_deviceTest.log"

    # Set up logging to file and console.
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s %(levelname)s: %(message)s', 
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # --- Rollcall Phase ---
    unresponsive_pis = []
    for host in pi_hosts:
        try:
            if not check_online(host):
                logging.info(f"{host} is unresponsive.")
                unresponsive_pis.append(host)
        except Exception as e:
            logging.error(f"An error occurred for {host}: {e}")
            unresponsive_pis.append(host)

    if unresponsive_pis:
        print("The following Pis could not connect:")
        for pi in unresponsive_pis:
            print(pi)
    else:
        print("All Pis connected successfully.")
    print("Roll call completed.\n")

    # --- Camera Check Phase ---
    noncamera_pis = []
    for pi_num in range(1, 21):
        try:
            if not check_cameras(pi_num):
                logging.info(f"pi{pi_num} has no camera.")
                noncamera_pis.append(pi_num)
        except Exception as e:
            logging.error(f"An error occurred for pi{pi_num}: {e}")
            noncamera_pis.append(pi_num)

    if noncamera_pis:
        print("The following Pis detected no camera:")
        for pi in noncamera_pis:
            print(f"pi{pi}")
    else:
        print("All Pis have cameras attached.")
    print("Camera check completed.\n")

    # --- IR Sensor Test Phase ---
    noIR_pis = []
    for pi_num in range(1, 21):
        try:
            if not check_ir_sensor(pi_num):
                logging.info(f"pi{pi_num} has a non-functioning IR sensor.")
                noIR_pis.append(pi_num)
        except Exception as e:
            logging.error(f"An error occurred during IR sensor test for pi{pi_num}: {e}")
            noIR_pis.append(pi_num)

    if noIR_pis:
        print("The following Pis have non-functioning IR sensors:")
        for pi in noIR_pis:
            print(f"pi{pi}")
    else:
        print("All IR sensors are functioning correctly.")
    print("IR sensor test completed.\n")

    print("Device tests completed.")

