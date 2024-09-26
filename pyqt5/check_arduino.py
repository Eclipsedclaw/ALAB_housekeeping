# Author: Jiancheng Zeng(JC)
# Date: June 7th, 2024

import time
import pymysql
from datetime import datetime
from time import sleep
import serial
from serial.tools import list_ports
import RPi.GPIO as GPIO
import math
from lazyins import Cursor
import os
from gpiozero import LED
import signal

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

# convert rtd digitized ADC into Kelvin temperature
def convert_RTD_ADC(x, offset):
    try:
        # Validate input x
        x_float = float(x)
    except ValueError:
        #print("Error: Input 'x' is not a valid numeric value.")
        return False

    try:
        # Validate input offset
        offset_float = float(offset)
    except ValueError:
        #print("Error: Input 'offset' is not a valid numeric value.")
        return False

    # Perform the calculations
    try:
        L_V = x_float * (5.0 / 1023.0)
        if(L_V == 5.0):
            return False
        else:
            L_R = L_V * 1000. / (5.0 - L_V)
            L_tmp = -(math.sqrt(17.59246 - 0.00232 * L_R) - 3.908) / 0.00116
            L_tmpK = L_tmp + 273.15
            L_correction = L_tmpK + offset_float  # No correction for now
            return round(float(L_correction), 2)    # Round to 2 digits
    except Exception as e:
        print(f"Error during data querying")
        return False

# This function query rtd readout from arduino and send to mysql database
def get_rtd():
    # Set the signal handler and a timeout alarm
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(2)

    print("Getting RTD data now...")
    try:
        cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'LAr_TPCruns_data', table_name = 'arduino_240723')
        print("Host is " + str(os.environ.get('LAZYINS_HOST')))
        # table for pressure in db
        name_rtd = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5']
        types_rtd = ['FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT']
        ardpath = "/dev/arduino"
        arduino = serial.Serial(ardpath)
        arduino.baudrate = 9600
        arduino.parity = 'N'
        arduino.stopbits = 1
        arduino.bytesize = 8

        sleep(1)
        try:
            RTD = arduino.readline().decode('utf8')

            print("RTD is: ", RTD)
            if(RTD[3:7] == '' or convert_RTD_ADC(RTD[3:7], 0) == False):
                R0 = None
            else:
                R0 = convert_RTD_ADC(float(RTD[3:7]), -1)    # (ADC number, offset)
            #print("R0 is " + str(R0) + "K")

            if(RTD[11:15] == '' or convert_RTD_ADC(RTD[11:15], 0) == False):
                R1 = None
            else:
                R1 = convert_RTD_ADC(float(RTD[11:15]), -1)    # (ADC number, offset)
            #print("R1 is " + str(R1) + "K")

            if(RTD[19:23] == '' or convert_RTD_ADC(RTD[19:23], 0) == False):
                R2 = None
            else:
                R2 = convert_RTD_ADC(float(RTD[19:23]), -2)    # (ADC number, offset)
            #print("R2 is " + str(R2) + "K")

            if(RTD[27:31] == '' or convert_RTD_ADC(RTD[27:31], 0) == False):
                R3 = None
            else:
                R3 = convert_RTD_ADC(float(RTD[27:31]), -2)    # (ADC number, offset)
            #print("R3 is " + str(R3) + "K")

            if(RTD[35:39] == '' or convert_RTD_ADC(RTD[35:39], 0) == False):
                R4 = None
            else:
                R4 = convert_RTD_ADC(float(RTD[35:39]), -3)    # (ADC number, offset)
            #print("R4 is " + str(R4) + "K")

            if(RTD[43:47] == '' or convert_RTD_ADC(RTD[43:47], 0) == False):
                R5 = None
            else:
                R5 = convert_RTD_ADC(float(RTD[43:47]), 2)    # (ADC number, offset)
            #print("R5 is " + str(R5) + "K")

            values_rtd = [R0, R1, R2, R3, R4, R5]

            #if(R0 != None and R1 != None and R2 != None and R3 != None and R4 != None and R5 != None):
                # insert
            cursor.setup(name_rtd, types = types_rtd)
            cursor.register(values_rtd)

            print("Current rtd leveling sensors: ",values_rtd)
            return values_rtd
        except TimeoutException:
            RTD = "Read timed out"
    except Exception as e:
        print("Error in try block:", e)
        #print("rtd data querying error")
        pass
        return None

get_rtd()