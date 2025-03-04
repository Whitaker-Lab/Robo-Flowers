import os
import sys
import time
from datetime import datetime
import subprocess
import logging

def check_online(hostname):
    """
    Check if a device is online by pinging it.
    """
    try:
        output = subprocess.check_output(['ping', '-c', '1', hostname], stderr=subprocess.STDOUT, universal_newlines=True)
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
    hostname = f"pi{pi_num}.wifi.edu" #replace this with your own hostname pattern
    username = f"pi{pi_num}"
    try:

        # SSH into the host and run `lsusb` to check for USB devices
        lsusb_cmd = f"ssh {username}@{hostname} lsusb"  
        usb_output = subprocess.check_output(lsusb_cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        
        # Look for keywords that typically indicate a USB camera in lsusb output
        has_camera = any(keyword in usb_output.lower() for keyword in ["camera", "pixel"])

        if has_camera:
            logging.info(f"{hostname} has a USB camera connected.")
        else:
            logging.warning(f"No USB camera detected on {hostname}.")
        
        return has_camera

    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to check USB devices on {hostname}: {e.output}")
        return False


if __name__ == "__main__":

    pi_hosts = [f"pi{i}.wifi.etsu.edu" for i in range(1, 21)]
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H%M%S")

    # Create and declare directories
    local_directory = "/home/rpimain/Data"
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    log_directory = "rollCall_logFiles"  # Updated log directory name
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_filename = f"{log_directory}/{current_date}_{current_time}_deviceTest.log"

    # Set up logging to file and console
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ])

    # Rollcall phase
    unresponsive_pis = []
    for host in pi_hosts:
        try:
            if not check_online(host):
                logging.info(f"{host} is unresponsive.")
                unresponsive_pis.append(host)
        except Exception as e:
            logging.error(f"An error occurred for {host}: {e}")
            unresponsive_pis.append(host)

    # Print list of unresponsive Pis to the console
    if unresponsive_pis:
        print("The following Pis could not connect:")
        for pi in unresponsive_pis:
            print(pi)
    else:
        print("All Pis connected successfully.")

    print("Roll call completed.")

    # Camera check phase
    noncamera_pis = []
    for pi_num in range(1,21):
        try:
            if not check_cameras(pi_num):
                logging.info(f"{pi_num} has no camera.")
                noncamera_pis.append(pi_num)
        except Exception as e:
            logging.error(f"An error occurred for {pi_num}: {e}")
            noncamera_pis.append(pi_num)

    # Print list of Pis with no camera to the console
    if noncamera_pis:
        print("The following Pis detected no camera:")
        for pi in noncamera_pis:
            print(pi)

    print("Camera check completed.")
