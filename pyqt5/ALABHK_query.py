# Author: Jiancheng Zeng(JC)
# Date: May 5th, 2024

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


def do_nothing(x):
    return x


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

def compressor_ON():
    # Fixed compressor address, configured by Robin
    compresspath = "/dev/compress"
    Compressor = serial.Serial(compresspath)
    
    # Standard baud rates include 110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000 and 256000 bits per second.
    Compressor.baudrate = 9600
    Compressor.parity = 'N'
    Compressor.stopbits = 1
    Compressor.bytesize = 8

    Compressor.write(b'$ON177CF\r')
    time.sleep(0.1)
    print("\nCompressor is ON!\n")
    return

def compressor_OFF():
    # Fixed compressor address, configured by Robin
    compresspath = "/dev/compress"
    Compressor = serial.Serial(compresspath)
    
    # Standard baud rates include 110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000 and 256000 bits per second.
    Compressor.baudrate = 9600
    Compressor.parity = 'N'
    Compressor.stopbits = 1
    Compressor.bytesize = 8

    Compressor.write(b'$OFF9188\r')
    time.sleep(0.1)
    print("\nCompressor is OFF!\n")
    return

# This function query compressor status and send to mysql database
def get_compressor():
    print("Getting compressor data now...")
    try:
        # Keita's module for eazy sql input
        cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'LAr_TPCruns_data', table_name = 'compressor')

        # table for compressor in db, currently shows compressor temperature T1/T2/T3
        name_compressor = ['T1', 'T2', 'T3', 'P_Return']
        types_compressor = ['int', 'int', 'int', 'int']

        # Fixed compressor address, configured by Robin
        compresspath = "/dev/compress"
        Compressor = serial.Serial(compresspath)
        
        # Standard baud rates include 110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000 and 256000 bits per second.
        Compressor.baudrate = 9600
        Compressor.parity = 'N'
        Compressor.stopbits = 1
        Compressor.bytesize = 8

        # Compressor temperature
        Compressor.write(b'$TEAA4B9\r')
        # Todo: figure out why it need to sleep for a certain amount of time
        sleep(0.5)
        CompressorOut_T = Compressor.read(Compressor.inWaiting()).decode('utf8')

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
        Compressor.write(b'$PRA95F7\r')
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

        print("Current compressor status['T1', 'T2', 'T3', 'P_R']: ", values_compressor)
        return values_compressor
    # If can't connect to database, drop this query
    except Exception as e:
        print("Error in try block:", e)
        pass
        return None


# This function query pressure data from the pressure gauge and send to mysql database
def get_pressure():
    print("Getting pressure data now...")

    try:
        cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'LAr_TPCruns_data', table_name = 'pressure')

        # table for pressure in db
        name_pressure = ['chamber_pressure', 'jacket_pressure']
        types_pressure = ['float', 'float']

        # Fixed pressure gauge value, configured by Robin
        chamberpressurepath = "/dev/toppress"
        chamberPressure = serial.Serial(chamberpressurepath)
        chamberPressure.baudrate = 9600
        chamberPressure.parity = 'N'
        chamberPressure.stopbits = 1
        chamberPressure.bytesize = 8
        chamberPressure.write(('@001PR3?;FF').encode('utf8'))

        sleep(0.1)

        try:
            ChamberPressureOut = chamberPressure.read(chamberPressure.inWaiting()).decode('utf8')
            chamber_pressure = float(ChamberPressureOut[7:14])
        except Exception as e:
            print("Error in chamber pressure query:", e)
            chamber_pressure = None
        finally:
            # Ensure the port is closed properly
            chamberPressure.close()


        # Fixed pressure gauge value, configured by Robin
        jacketpressurepath = "/dev/botpress"
        jacketPressure = serial.Serial(jacketpressurepath)
        jacketPressure.baudrate = 9600
        jacketPressure.parity = 'N'
        jacketPressure.stopbits = 1
        jacketPressure.bytesize = 8
        jacketPressure.write(('@002PR3?;FF').encode('utf8'))

        # Todo: figure out why somehow it need to sleep for a certain time to readout normally
        sleep(0.1)

        try:
            JacketPressureOut = jacketPressure.read(jacketPressure.inWaiting()).decode('utf8')
            jacket_pressure = float(JacketPressureOut[7:14])
        except Exception as e:
            print("Error in jacket pressure query:", e)
            jacket_pressure = None

        values_pressure = [chamber_pressure, jacket_pressure]

        # insert
        cursor.setup(name_pressure, types = types_pressure)
        cursor.register(values_pressure)

        print("Current pressure: ", values_pressure)
        return values_pressure
    except Exception as e:
        print("Error in pressure query:", e)
        pass
        return None

# This function query rtd readout from arduino and send to mysql database
def get_rtd():
    print("Getting RTD data now...")
    try:
        cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'LAr_TPCruns_data', table_name = 'rtd')
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

        sleep(0.1)

        RTD = arduino.readline().decode('utf8')
        print("RTD is: ", RTD)
        print("convert is: ", convert_RTD_ADC(RTD[3:7], 0))
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
    except Exception as e:
        print("Error in try block:", e)
        #print("rtd data querying error")
        pass
        return None

def HeaterON(GPIO_pin):
    try:
        GPIO.output(GPIO_pin, GPIO.HIGH)
    except:
        Heater_control = LED(GPIO_pin)
        Heater_control.blink(on_time=100, off_time=0.01)
    time.sleep(0.1)
    print("\nHeaters are ON!\n")
    return

def HeaterOFF(GPIO_pin):
    try:
        Heater_control = LED(pin=GPIO_pin)
        Heater_control.off()
    except:
        GPIO.output(GPIO_pin, GPIO.LOW)
    time.sleep(0.1)
    print("\nHeaters are OFF!\n")
