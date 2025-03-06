#!/bin/bash

#all pis are running 32GB SD cards loaded with the Raspberry Pi OS Lite, Release date: November 19th 2024, System: 32-bit, Kernel version: 6.6, Debian version: 12 (bookworm)
#ssh was enabled during SD card setup and confirmed by checking the ssh file present in the /bootfs directory (otherwise it was created there).  

# Loop through Raspberry Pi numbers from 1 to 20
for i in {1..20}; do
    host="pi$i.wifi.etsu.edu"

    echo "Checking connectivity to $host..."
    if ! ping -c 1 -W 2 "$host" >/dev/null; then
        echo "Skipping $host (not reachable)"
        continue
    fi

    echo "Changing settings on $host"
    
    # Update and install necessary packages locally
    sudo apt update && sudo apt upgrade -y
    echo "Finished Updating"

    sudo apt install -y screen python3-numpy python3-pandas python3-opencv python3-rpi-lgpio
    echo "Finished installing python packages (opencv, pandas, numpy), GPIO, and screen"
    
    # Check if rpi-connect-lite exists before attempting installation
    if apt-cache show rpi-connect-lite &>/dev/null; then
        sudo apt install -y rpi-connect-lite
        rpi-connect on
	loginctl enable-linger
        echo "Finished rpi-connect"
    else
        echo "rpi-connect-lite not found, skipping installation"
    fi

    # Execute locale setting commands on the remote Pi
    ssh -o ConnectTimeout=5 pi$i@$host "bash -s" <<'EOF'
    set -e  # Exit script on any error

    echo "Enabling SSH..."
    sudo touch /boot/ssh

    # Desired locale
    DESIRED_LOCALE="en_US.UTF-8"
    
    sudo apt-get install -y locales
    
    # Temporarily unset locale to avoid warnings during locale generation
    unset LANG LANGUAGE LC_CTYPE LC_NUMERIC LC_TIME LC_COLLATE LC_MONETARY \
          LC_MESSAGES LC_PAPER LC_NAME LC_ADDRESS LC_TELEPHONE LC_MEASUREMENT \
          LC_IDENTIFICATION LC_ALL
    
    # Generate the desired locale if missing
    sudo locale-gen "$DESIRED_LOCALE"
    
    # Ensure the locale is properly generated
    if ! sudo locale -a | grep -q "$DESIRED_LOCALE"; then
        echo "Failed to generate locale $DESIRED_LOCALE"
        exit 1
    fi

    # Update /etc/default/locale with the desired locale
    sudo bash -c "cat > /etc/default/locale <<EOF2
LANG=\"$DESIRED_LOCALE\"
LANGUAGE=\"en_US:en\"
LC_ALL=\"$DESIRED_LOCALE\"
EOF2"

    # Reconfigure locales
    sudo DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales
    
    # Source the locale file to apply settings to the current session
    source /etc/default/locale
    
    # Check current locale settings
    locale
    
    echo "Locale settings have been updated successfully. Rebooting..."
    sudo reboot
EOF

done

# Wait for all background processes to complete
wait
echo "Settings updated and all reachable Raspberry Pis are rebooting."
