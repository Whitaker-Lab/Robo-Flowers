import os
import sys
import time
from datetime import datetime
import subprocess
import logging
import pandas as pd


#add functionality to provide user input as to the color/treatment of each pi, which is then added to the resulting csv files

#paths & directories
IRScript = ''  # Path to the IRscript on the Control Pi
CameraScript = '' # Path to the Camera on the Control Pi

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

def send_scripts_to_pi(pi_num, IRScript, CameraScript):
    """
    Executes a script on a remote Pi using SSH within a screen session.
    """
    hostname = f"pi{pi_num}.wifi.etsu.edu" #replace with hostname pattern
    username = f"pi{pi_num}"
    
    try:
        #Copy the script to the remote Pi
        scp_command1 = f"scp {IRScript} {username}@{hostname}:/home/{username}/IRScript.py"
        subprocess.check_call(scp_command1, shell=True)
        print(f"IRScript sent to {hostname}.")
        logging.info(f"IRScript sent to {hostname}.")

        scp_command2 = f"scp {CameraScript} {username}@{hostname}:/home/{username}/CameraScript.py"
        subprocess.check_call(scp_command2, shell=True)
        print(f"CameraScript sent to {hostname}.")
        logging.info(f"CameraScript sent to {hostname}.")
    except subprocess.CalledProcessError as e:
        print(f"Error sending scripts to {hostname}: {e}")
        logging.error(f"Error sending scripts to {hostname}: {e}")


def execute_scripts_on_pi(pi_num, IRScript, CameraScript):
    """
    Executes IR and camera scripts concurrently on a remote Pi using SSH within a screen session.
    """
    hostname = f"pi{pi_num}.wifi.etsu.edu"
    username = f"pi{pi_num}"

    try:

        # Start the script in a detached screen session
        ssh_command = f"""
            ssh {username}@{hostname} '
                screen -dmS Scripts_{pi_num} bash -c "
                    screen -t IRScript python3 /home/{username}/IRScript.py;
                    screen -t CameraScript python3 /home/{username}/CameraScript.py
                "
            '
        """
        subprocess.check_call(ssh_command, shell=True)

        print(f"Scripts executed concurrently on {hostname} in a screen session.")
        logging.info(f"Scripts executed concurrently on {hostname} in a screen session.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing scripts on {hostname}: {e}")
        logging.error(f"Error executing scripts on {hostname}: {e}")

# Function to fetch CSV files from remote Pis
def fetch_csv_files(pi_hosts, local_directory):
    print("\nFetching CSV files from remote Pis for today's date...")
    current_date = datetime.now().strftime("%Y-%m-%d")
    for host in pi_hosts:
        user = host.split('.')[0]  # Extract username from hostname
        remote_directory = f"/home/{user}/RawData"  # Remote directory where CSV files are stored
        try:
            # Use scp to fetch the files
            subprocess.run(
                ["scp", f"{user}@{host}:{remote_directory}/{current_date}*.csv", local_directory],
                check=True
            )
            print(f"Fetched files from {host}.")
        except subprocess.CalledProcessError as e:
            print(f"Error fetching files from {host}: {e}")


# Function to cleanup by terminating all screen sessions on remote Pis
def cleanup(pi_hosts):
    print("\nPerforming cleanup...")
    for host in pi_hosts:
        user = host.split('.')[0]  # Extract username from hostname
        try:
            subprocess.run(
                ["ssh", f"{user}@{host}", "pkill", "screen"],
                check=True
            )
            print(f"Screen sessions terminated on {host}.")
        except subprocess.CalledProcessError as e:
            print(f"Error terminating screen sessions on {host}: {e}")


if __name__ == "__main__":

    pi_hosts = [f"pi{i}.wifi.etsu.edu" for i in range(1, 21)]
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H%M%S")

    # Create and declare directories
    local_directory = "/home/rpimain/Data"
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)

    log_directory = "rollCall_logFiles"  # Updated log directory name (where are these being saved?)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_filename = f"{log_directory}/{current_date}_{current_time}_rollCall.log"

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
        #sys.exit(1)
    else:
        print("All Pis connected successfully.")

    print("Roll call completed.")

    
     # Send scripts to each Pi
    for pi_num in range(1, 21):
        send_scripts_to_pi(pi_num, IRScript, CameraScript)

     # Execute scripts on each Pi
    for pi_num in range(1, 21):
        execute_scripts_on_pi(pi_num, IRScript, CameraScript)

    print("All scripts started on Pis.")

    # Wait for the duration of the long-running task
    duration = 12 * 3600  # 12 hours in seconds (3600 seconds per hour)
    print("\nWaiting for 12 hours ...")
    time.sleep(duration)


   # Fetch CSV files from remote Pis
    fetch_csv_files(pi_hosts, local_directory)

    # Perform cleanup by terminating all screen sessions on remote Pis
    cleanup(pi_hosts)

    print("All screen sessions terminated.")
    logging.info("All screen sessions terminated.")

