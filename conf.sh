#!/bin/bash

# Check if the script is being run as root
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root. Re-executing with sudo..."
  sudo "$0" "$@"
  exit
fi

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "Udev rule added successfully."
else
    echo "Failed to add udev rule."
    exit 1
fi

# Reload udev rules to apply the changes
sudo /etc/init.d/udev restart  

# Trigger the rules to apply to already connected devices
sudo udevadm trigger

# Get the original user's home directory (even when run with sudo)
REAL_USER=$(who am i | awk '{print $1}')
USER_HOME=$(getent passwd "$REAL_USER" | cut -d: -f6)
BASH_RC="$USER_HOME/.bashrc"

# Function to add/update a variable in .bashrc
update_bashrc() {
  local var_name="$1"
  local var_value="$2"
  
  if grep -q "export $var_name=" "$BASH_RC"; then
    # Update existing variable
    if sed -i "/export $var_name=/c\export $var_name=\"$var_value\"" "$BASH_RC"; then
      echo "[SUCCESS] Updated $var_name in $BASH_RC"
    else
      echo "[ERROR] Failed to update $var_name" >&2
      return 1
    fi
  else
    # Add new variable
    if echo "export $var_name=\"$var_value\"" >> "$BASH_RC"; then
      echo "[SUCCESS] Added $var_name to $BASH_RC"
    else
      echo "[ERROR] Failed to add $var_name" >&2
      return 1
    fi
  fi
}

# Prompt for inputs
read -p "Please enter the hostname: " hostname
update_bashrc "LAZYINS_HOST" "$hostname"

read -p "Please enter the MySQL listening port: " port
update_bashrc "LAZYINS_PORT" "$port"

read -p "Please enter the MySQL username: " username
update_bashrc "LAZYINS_USER" "$username"

# WARNING: Storing passwords in .bashrc is insecure!
read -p "Please enter the MySQL password: " passwd
update_bashrc "LAZYINS_PASSWD" "$passwd"

# Notify user to reload
echo -e "\nChanges written to $BASH_RC"
echo "Run 'source ~/.bashrc' or restart your terminal to apply changes."

# Check if the darabase commands was successful
if [ $? -eq 0 ]; then
    echo "database information added successfully."
else
    echo "Failed to add database information"
    exit 1
fi

#install required modules
pip install pymysql --break-system-packages
pip install lazyins --break-system-packages
pip install mysql-connector-python-rf --break-system-packages
pip install mysql-connector-python --break-system-packages
