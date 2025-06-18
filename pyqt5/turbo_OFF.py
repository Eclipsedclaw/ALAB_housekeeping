import time
import pymysql
from datetime import datetime
from time import sleep
import serial
from serial.tools import list_ports
#import RPi.GPIO as GPIO
import math
from lazyins import Cursor
import os
#from gpiozero import LED
import signal

# This function query compressor status and send to mysql database
def get_compressor():
    print("Getting turbo feedback now...")
    try:
        """
        # TODO: make this input user determined
        compresspath = "/dev/ttyACM1"
        Compressor = serial.Serial(compresspath)
        
        # Standard baud rates include 110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000 and 256000 bits per second.
        Compressor.baudrate = 9600
        Compressor.parity = 'N'
        Compressor.stopbits = 1
        Compressor.bytesize = 8

        # Compressor temperature
        Compressor.write(b'0010030902=?107\r')
        # Todo: figure out why it need to sleep for a certain amount of time
        sleep(1)
        #CompressorOut_T = Compressor.readline().decode('utf8')
        CompressorOut_T = Compressor.read(Compressor.inWaiting()).decode('utf8')
        print("Readout is: ",CompressorOut_T)

        """

        compresspath = "/dev/ttyUSB1"
        Compressor = serial.Serial(compresspath, baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=2)
        
        base_command = '0011001006000000'
        
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
    
# search serial port
ser = serial.Serial()
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)

try:
    temp_value = get_compressor()
    time.sleep(1)  # Delay for 0.1 second
except KeyboardInterrupt:
    print("Process interrupted by the user.")