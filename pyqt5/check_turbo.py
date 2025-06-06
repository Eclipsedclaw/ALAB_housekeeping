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

# This function query compressor status and send to mysql database
def get_compressor():
    print("Getting compressor data now...")
    try:
        # Keita's module for eazy sql input
        cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'LAr_TPCruns_data', table_name = 'compressor')

        # table for compressor in db, currently shows compressor temperature T1/T2/T3
        name_compressor = ['T1', 'T2', 'T3', 'P_Return']
        types_compressor = ['int', 'int', 'int', 'int']

        # TODO: make this input user determined
        compresspath = "/dev/cu.usbmodem585A0502411"
        Compressor = serial.Serial(compresspath)
        
        # Standard baud rates include 110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000 and 256000 bits per second.
        Compressor.baudrate = 9600
        Compressor.parity = 'N'
        Compressor.stopbits = 1
        Compressor.bytesize = 8

        # Compressor temperature
        Compressor.write(b'9500030902=?120\r')
        # Todo: figure out why it need to sleep for a certain amount of time
        sleep(2)
        CompressorOut_T = Compressor.read(Compressor.inWaiting()).decode('utf8')
        print("Readout is: ",CompressorOut_T)
        # This is to check whether there is any values properly read
        if(CompressorOut_T[6:8] == ''):
            T1_temp = None
        else:
            T1_temp = CompressorOut_T[6:8]
        if(CompressorOut_T[10:12] == ''):
            T2_temp = None
        else:
            T2_temp = CompressorOut_T[10:12]
        if(CompressorOut_T[14:16] == ''):
            T3_temp = None
        else:
            T3_temp = CompressorOut_T[14:16]

        # Compressor return pressure
        #Compressor.write(b'$PRA95F7\r')
        # Todo: figure out why it need to sleep for a certain amount of time
        sleep(0.5)
        CompressorOut_P = Compressor.read(Compressor.inWaiting()).decode('utf8')

        if(CompressorOut_P[5:8] == ''):
            P_R_temp = None
        else:
            P_R_temp = CompressorOut_P[5:8]

        values_compressor = [T1_temp, T2_temp, T3_temp, P_R_temp]

        # insert data to mysql database
        cursor.setup(name_compressor, types = types_compressor)
        cursor.register(values_compressor)

        #print("Current compressor status['T1', 'T2', 'T3', 'P_R']: ", values_compressor)
        return values_compressor
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
    while True:
        temp_value = get_compressor()
        print("this query readout is: ",temp_value)
        time.sleep(1)  # Delay for 0.1 second
except KeyboardInterrupt:
    print("Process interrupted by the user.")