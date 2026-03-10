# Author: Jiancheng Zeng(JC), Junwen Zheng
# Date: July 30, 2025

import time
from time import sleep
import serial
from serial.tools import list_ports

# search serial port and let the users choose the port for the turbo
ser = serial.Serial()
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)
device = input("Input the USB port number:")

# let the user choose which control command they want to operate
# Options could include: start, stop, setting values, etc.
control_command = input("Please choose a control command. Type 1 for start, 2 for stop, 3 for confirming the nominal rotation speed: ")

# This function controls the turbo
def control_turbo():
    print("Getting turbo feedback now...")
    try:
        turbopath = "/dev/ttyUSB" + device
        Turbo = serial.Serial(turbopath, baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=2)
        
        if control_command == "1":
            base_command = '0011001006111111'
        elif control_command == "2":
            base_command = '0011001006000000'
        elif control_command == "3":
            turbo_type = input("Is the turbo HiPace 300? (y/n):")
            if turbo_type == "y": 
                base_command = '0011077706001000'
            else:
                base_command = '0011077706000820'

        # Calculate checksum: sum of ASCII values modulo 256
        checksum = sum(ord(c) for c in base_command) % 256
        
        command = f'{base_command}{checksum:03d}\r'

        Turbo.write(command.encode('ascii'))

        print(f"command : {command}")
        sleep(2)
        # Read response (adjust size or use readline())
        response = Turbo.read(100)  # Or: Turbo.readline()
        print("Start Raw bytes:", response)
        print("Decoded:", response.decode('ascii', errors='ignore'))
        TurboOUT = response.decode('ascii', errors='ignore')
        print("TurboOUT is: ", TurboOUT)

        if control_command == "1":
            print("Starting turbo...")
        elif control_command == "2":
            print("Stopping turbo...")
        elif control_command == "3":
            print("Confirming nominal rotation speed...")

    except Exception as e:
        print("Error in try block:", e)
        pass
        return None
    

try:
    control_turbo()
    time.sleep(1)  # Delay for 0.1 second
except KeyboardInterrupt:
    print("Process interrupted by the user.")