import subprocess
import os
import sys
import csv
import socket
from datetime import datetime
import logging

def check_online(hostname):
    """
    Check if a device is online by pinging it and return its IP address if available.
    """
    try:
        output = subprocess.check_output(['ping', '-c', '1', hostname], stderr=subprocess.STDOUT, universal_newlines=True)
        if "1 received" in output:
            logging.info(f"{hostname} is online.")
            # Try to fetch IP using 'dig' command
            try:
                dig_output = subprocess.check_output(['dig', '+short', hostname], stderr=subprocess.STDOUT, universal_newlines=True).strip()
                ip_address = dig_output.split('\n')[0] if dig_output else "Unknown"
            except Exception:
                # Fallback to socket lookup
                try:
                    ip_address = socket.gethostbyname(hostname)
                except socket.gaierror:
                    ip_address = "Unknown"
            return True, ip_address
        else:
            logging.error(f"{hostname} is offline.")
            return False, ""
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to ping {hostname}: {e.output}")
        return False, ""
    except Exception as e:
        logging.error(f"An error occurred for {hostname}: {e}")
        return False, ""

if __name__ == "__main__":
    pi_hosts = [f"pi{i}.wifi.etsu.edu" for i in range(1, 21)]
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    csv_filename = f"/home/rpimain/RpiConnectionData.csv"

    # Check if the CSV file exists; if not, create it with headers
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Date", "Time", "Hostname", "Status", "IP Address"])

        # Rollcall phase
        unresponsive_pis = []
        for host in pi_hosts:
            is_online, ip_address = check_online(host)
            status = "Online" if is_online else "Offline"
            writer.writerow([current_date, current_time, host, status, ip_address])
            if not is_online:
                unresponsive_pis.append(host)
    
    # Print unresponsive Pis to console
    if unresponsive_pis:
        print("The following Pis could not connect:")
        for pi in unresponsive_pis:
            print(pi)
        sys.exit(1)
    else:
        print("All Pis connected successfully.")
        sys.exit(0)
    print("Roll call completed. Results appended to rollCall_results.csv.")


