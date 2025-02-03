import os
import sys
import time
from datetime import datetime
import subprocess
import logging
import pandas as pd


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

    cleanup(pi_hosts)


