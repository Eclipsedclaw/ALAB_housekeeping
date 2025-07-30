# Author: Jiancheng Zeng(JC)
# Date: Jan 2nd, 2025

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
        # Keita's module for eazy sql input
        cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'bench_test', table_name = 'turbo')

        # table for compressor in db, currently shows compressor temperature T1/T2/T3
        name_turbo = ['ActualSpd']
        types_turbo = ['int']
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

        compresspath = "/dev/ttyUSB"+device
        Compressor = serial.Serial(compresspath, baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=2)
        
        # telegram command sent to the turbo:
        # 001: address, 00: read (01:control/read back), 309:actual rotation speed, 02:the digit of the readout, =?: query, 107: sum of ASCII values of previous units modulo 256
        
        # Send command with correct checksum and carriage return
        base_command = '0010030902=?'
        
        # Calculate checksum: sum of ASCII values modulo 256
        checksum = sum(ord(c) for c in base_command) % 256
        
        command = f'{base_command}{checksum:03d}\r'
        
        Compressor.write(command.encode('ascii'))

        print(f"command : {command}")
        
        # Wait for response
        sleep(0.5)


        # Read response (adjust size or use readline())
        response = Compressor.read(100)  # Or: Compressor.readline()
        print("RPM Raw bytes:", response)
        print("Decoded:", response.decode('ascii', errors='ignore'))
        TurboOUT = response.decode('ascii', errors='ignore')


        # This is to check whether there is any values properly read
        if(TurboOUT[10:16] == ''):
            rpm_temp = None
        else:
            rpm_temp = TurboOUT[10:16]

        # Compressor return pressure
        #Compressor.write(b'$PRA95F7\r')
        # Todo: figure out why it need to sleep for a certain amount of time
        

        values_turbo = [rpm_temp]

        # insert data to mysql database
        cursor.setup(name_turbo, types = types_turbo)
        cursor.register(values_turbo)
        
        print("Current turbo status['rpm']: ", values_turbo)

        Compressor.close()
        return values_turbo
    # If can't connect to database, drop this query
    except Exception as e:
        print("Error in try block:", e)
        pass
        return None
    

try:
    while True:
        temp_value = get_compressor()
        #print("this query readout is: ",temp_value)
        time.sleep(1)  # Delay for 0.1 second
except KeyboardInterrupt:
    print("Process interrupted by the user.")