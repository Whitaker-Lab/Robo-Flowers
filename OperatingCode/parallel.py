import os
import sys
import time
import argparse
from datetime import datetime
import subprocess
import logging
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# Script paths (local machine)
IRScript = '/home/rpimain/Scripts/IR_Recording.py'
CameraScript = '/home/rpimain/Scripts/20241114_Camera.py'
RollCallScript = '/home/rpimain/Scripts/BetterRollCall.py'

def get_pi_credentials(pi_num):
    username = f"pi{pi_num}"
    hostname = f"{username}.wifi.etsu.edu"
    return username, hostname

def check_file_exists(pi_num, remote_path):
    username, hostname = get_pi_credentials(pi_num)
    check_command = f"ssh {username}@{hostname} '[ -f {remote_path} ] && echo Exists || echo Missing'"
    try:
        result = subprocess.check_output(check_command, shell=True, text=True).strip()
        return result == "Exists"
    except subprocess.CalledProcessError:
        return False

def send_scripts_to_pi(pi_num, ir_only=False):
    username, hostname = get_pi_credentials(pi_num)
    scripts_to_send = [(IRScript, "IR_Recording.py")]
    if not ir_only:
        scripts_to_send.append((CameraScript, "CameraScript.py"))

    for script, remote_name in scripts_to_send:
        remote_path = f"/home/{username}/{remote_name}"
        if not check_file_exists(pi_num, remote_path):
            try:
                scp_command = f"scp {script} {username}@{hostname}:{remote_path}"
                subprocess.check_call(scp_command, shell=True)
                print(f"{remote_name} sent to {hostname}.")
                logging.info(f"{remote_name} sent to {hostname}.")
            except subprocess.CalledProcessError as e:
                print(f"Error sending {remote_name} to {hostname}: {e}")
                logging.error(f"Error sending {remote_name} to {hostname}: {e}")

def execute_scripts_on_pi(pi_num, ir_only=False):
    username, hostname = get_pi_credentials(pi_num)
    commands = []
    commands.append((
        f"screen -dmS IRScript_{pi_num} bash -c 'mkdir -p Logs; python3 IR_Recording.py > Logs/IR_Recording.log 2>&1'",
        "IR_Recording.py"
    ))
    if not ir_only:
        commands.append((
            f"screen -dmS CameraScript_{pi_num} bash -c 'mkdir -p Logs; python3 CameraScript.py > Logs/CameraScript.log 2>&1'",
            "CameraScript.py"
        ))

    try:
        for cmd, script_name in commands:
            ssh_command = f"ssh {username}@{hostname} \"{cmd}\""
            subprocess.check_call(ssh_command, shell=True)
            print(f"{script_name} successfully started on {hostname}.")
            logging.info(f"{script_name} successfully started on {hostname}.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing scripts on {hostname}: {e}")
        logging.error(f"Error executing scripts on {hostname}: {e}")

def fetch_csv_files(pi_hosts, base_local_directory):
    current_date = datetime.now().strftime("%Y-%m-%d")
    local_directory = os.path.join(base_local_directory, current_date)
    os.makedirs(local_directory, exist_ok=True)

    print("\nFetching CSV files from remote Pis...")
    failed_fetches = []

    def fetch_from_host(host):
        user = host.split('.')[0]
        remote_directory = f"/home/{user}/Data"
        try:
            subprocess.run([
                "scp", f"{user}@{host}:{remote_directory}/{current_date}*.csv", local_directory
            ], check=True)
            print(f"Fetched files from {host}.")
        except subprocess.CalledProcessError:
            print(f"Error fetching files from {host}.")
            failed_fetches.append(host)

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(fetch_from_host, pi_hosts)

    if failed_fetches:
        print("\nThe following Pis failed to transfer CSV files:")
        for failed_host in failed_fetches:
            print(failed_host)

def cleanup(pi_hosts):
    print("\nPerforming cleanup...")

    def cleanup_host(host):
        user = host.split('.')[0]
        try:
            subprocess.run(["ssh", f"{user}@{host}", "pkill screen"], check=True)
            print(f"Screen sessions terminated on {host}.")
        except subprocess.CalledProcessError:
            print(f"Error terminating screen sessions on {host}.")

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(cleanup_host, pi_hosts)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control script for sending/executing IR and Camera scripts on Pis.")
    parser.add_argument('--ir-only', action='store_true', help='Only run the IR script (skip Camera script)')
    args = parser.parse_args()

    pi_hosts = [f"pi{i}.wifi.etsu.edu" for i in range(1, 21)]
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H%M%S")

    local_directory = "/home/rpimain/Data"

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', handlers=[
        logging.StreamHandler(sys.stdout)
    ])

    try:
        subprocess.check_call(["python3", RollCallScript])
    except subprocess.CalledProcessError:
        print("Roll call failed. Halting execution.")
        sys.exit(1)

    with ThreadPoolExecutor(max_workers=10) as executor:
        for pi_num in range(1, 21):
            executor.submit(send_scripts_to_pi, pi_num, args.ir_only)

    with ThreadPoolExecutor(max_workers=10) as executor:
        for pi_num in range(1, 21):
            executor.submit(execute_scripts_on_pi, pi_num, args.ir_only)

    print("All scripts started on Pis.")
    logging.info("All scripts started on Pis.")

    duration = 12 * 3600
    print("\nWaiting for 12 hours ...")
    time.sleep(duration)

    fetch_csv_files(pi_hosts, local_directory)
    cleanup(pi_hosts)

    print("All screen sessions terminated.")
    logging.info("All screen sessions terminated.")
