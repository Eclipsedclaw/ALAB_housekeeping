#!/bin/bash

# Check if the script is being run as root
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root. Re-executing with sudo..."
  sudo "$0" "$@"
  exit
fi

# setup USB port symlink
sudo bash -c 'echo "ACTION==\"add\", SUBSYSTEM==\"tty\", ATTRS{idVendor}==\"06cd\", ATTRS{idProduct}==\"0121\", SYMLINK+=\"toppress\"" >> /etc/udev/rules.d/99-myusb.rules'
sudo bash -c 'echo "ACTION=="add", SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0043", SYMLINK+="arduino"" >> /etc/udev/rules.d/99-myusb.rules'
sudo bash -c 'echo "ACTION=="add", SUBSYSTEM=="tty", ATTRS{serial}=="DCAWb115819", SYMLINK+="botpress"" >> /etc/udev/rules.d/99-myusb.rules'
sudo bash -c 'echo "ACTION=="add", SUBSYSTEM=="tty", ATTRS{serial}=="EJCZb11A920", SYMLINK+="compress"" >> /etc/udev/rules.d/99-myusb.rules'

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

# Prompt the user for the database hostname
read -p "Please enter the hostname: " hostname
# Add the hostname to database
sudo bash -c "echo 'export LAZYINS_HOST=\"$hostname\"' >> /home/pi/.bashrc"

# Prompt the user for the database port
read -p "Please enter the port: " port
# Add the hostname to database
sudo bash -c "echo 'export LAZYINS_PORT=\"$port\"' >> /home/pi/.bashrc"

# Prompt the user for the database username
read -p "Please enter the username: " username
# Add the hostname to database
sudo bash -c "echo 'export LAZYINS_USER=\"$username\"' >> /home/pi/.bashrc"

# Prompt the user for the database passwd
read -p "Please enter the password: " passwd
# Add the hostname to database
sudo bash -c "echo 'export LAZYINS_PASSWD=\"$passwd\"' >> /home/pi/.bashrc"

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

# reboot system
echo "Please reboot to let usb symlink work"