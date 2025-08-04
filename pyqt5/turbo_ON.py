# Author: Jiancheng Zeng(JC), Junwen Zheng
# Date: July 30, 2025

import time
from time import sleep
import serial
from serial.tools import list_ports

# search serial port
ser = serial.Serial()
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)
device = input("Input the USB port number(Not 0):")

# This function query compressor status and send to mysql database
def get_compressor():
    print("Getting turbo feedback now...")
    try:
        compresspath = "/dev/ttyUSB" + device
        Compressor = serial.Serial(compresspath, baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=2)
        
        base_command = '0011001006111111'
        
        # Calculate checksum: sum of ASCII values modulo 256
        checksum = sum(ord(c) for c in base_command) % 256
        
        command = f'{base_command}{checksum:03d}\r'
        
        Compressor.write(command.encode('ascii'))

        print(f"command : {command}")
        sleep(2)
        # Read response (adjust size or use readline())
        response = Compressor.read(100)  # Or: Compressor.readline()
        print("Start Raw bytes:", response)
        print("Decoded:", response.decode('ascii', errors='ignore'))
        TurboOUT = response.decode('ascii', errors='ignore')
        print("TurboOUT is: ", TurboOUT)
        

    # If can't connect to database, drop this query
    except Exception as e:
        print("Error in try block:", e)
        pass
        return None

try:
    temp_value = get_compressor()
    time.sleep(1)  # Delay for 0.1 second
except KeyboardInterrupt:
    print("Process interrupted by the user.")