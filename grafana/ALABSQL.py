# Author: Jiancheng Zeng(JC)
# Date: Dec 8th, 2023
import pymysql
from datetime import datetime
from time import sleep
import serial
from serial.tools import list_ports
#import RPi.GPIO as GPIO
import math
from lazyins import Cursor
import os
import re

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
            return float(L_correction)
    except Exception as e:
        #print(f"Error during calculation: {e}")
        return False


# This function query compressor status and send to mysql database
def get_compressor():
    try:
        # Keita's module for eazy sql input
        cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'pgrams', table_name = 'ground')

        # table for compressor in db, currently shows compressor temperature T1/T2/T3
        name_compressor = ['compressorT1', 'compressorT2', 'compressorT3']
        types_compressor = ['int', 'int', 'int']

        # Fixed compressor address, configured by Robind
        compresspath = "/dev/ttyUSB2"
        Compressor = serial.Serial(compresspath)
        # Standard baud rates include 110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000 and 256000 bits per second.
        Compressor.baudrate = 9600
        Compressor.parity = 'N'
        Compressor.stopbits = 1
        Compressor.bytesize = 8

        # Todo: figure out why it need to sleep for a certain amount of time
        sleep(0.1)

        Compressor.write(b'$TEAA4B9\r')
        CompressorOut = Compressor.read(Compressor.inWaiting()).decode('utf8')

        # This is to check whether there is any values properly read
        if(CompressorOut[6:8] == ''):
            T1_temp = None
        else:
            T1_temp = CompressorOut[6:8]
        if(CompressorOut[10:12] == ''):
            T2_temp = None
        else:
            T2_temp = CompressorOut[10:12]
        if(CompressorOut[14:16] == ''):
            T3_temp = None
        else:
            T3_temp = CompressorOut[14:16]

        values_compressor = [T1_temp, T2_temp, T3_temp]

        # insert data to mysql database
        cursor.setup(name_compressor, types = types_compressor)
        cursor.register(values_compressor)

        return
    # If can't connect to database, drop this query
    except:
        pass
        return


# This function query pressure data from the pressure gauge and send to mysql database
def get_pressure():

    #try:
    cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'pgrams', table_name = 'chamber')
    #cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'LAr_TPCruns_data', table_name = 'pressure')

    # table for pressure in db
    #name_pressure = ['chamber_pressure', 'jacket_pressure']
    name_pressure = [f'cp_PR{i+1}'for i in range(5) ]
    name_pressure += [f'jp_PR{i+1}'for i in range(5) ]
    #name_pressure = ['cp_PR1', 'jacket_pressure']
    types_pressure = ['float' for i in range(10)]

    # Fixed pressure gauge value, configured by Robin
    #chamberpressurepath = "/dev/ttyUSB1"
    #chamberPressure = serial.Serial(chamberpressurepath)
    #chamberPressure.baudrate = 9600
    #chamberPressure.parity = 'N'
    #chamberPressure.stopbits = 1
    #chamberPressure.bytesize = 8
    chamber_pressure = []
    for i in range(5):
    #    chamberPressure.write(('$@001PR3?;FF').encode('utf8'))
        chamber_pressure.append(0)

    #    sleep(0.1)

    #    ChamberPressureOut = chamberPressure.read(chamberPressure.inWaiting()).decode('utf8')
    #    if(ChamberPressureOut[7:14] == ''):
    #        chamber_pressure = None
    #    else:
    #        chamber_pressure = float(ChamberPressureOut[7:14])
    #        #print("chamber pressure is: " + str(chamber_pressure))
    #        #print(type(chamber_pressure))

    # Fixed pressure gauge value, configured by Robin
    jacketpressurepath = "/dev/ttyUSB0"
    jacketPressure = serial.Serial(jacketpressurepath)
    jacketPressure.baudrate = 115200
    jacketPressure.parity = 'N'
    jacketPressure.stopbits = 1
    jacketPressure.bytesize = 8
    jacket_pressure = []
    #jacketPressure.write(('$@253PR3?;FF').encode('utf8'))
    # edit 
    for i in range(3):
        jacketPressure.write((f'$@002PR{i+1}?;FF').encode('utf8'))

    # Todo: figure out why somehow it need to sleep for a certain time to readout normally
        sleep(0.1)

        JacketPressureOut = jacketPressure.read(jacketPressure.inWaiting()).decode('utf8')
        ret = re.split("@002ACK([0-9\\-\\+E\\.]*?);FF",JacketPressureOut)
        #print(ret[1])
        if(JacketPressureOut == ''):
            jacket_pressure.append(0)
        else:
            try:
                print(f"jacket pressure{i+1} is: " + str(ret[1]))
                jacket_pressure.append(float(ret[1]))
            except:
                print(f"jacket pressure{i+1} cannot be read: " + JacketPressureOut)
                jacket_pressure.append(0.0)
    for i in range(2):
        jacket_pressure.append(0.0)
    values_pressure = [*chamber_pressure, *jacket_pressure]

    # insert
    #cursor.setup(name_pressure, types = types_pressure)
    #cursor.register(values_pressure)

    #return
    #except:
    #    pass
    #    return

# This function query rtd readout from arduino and send to mysql database
#def get_rtd():
    #try:
        #cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'pgrams', table_name = 'chamber')

        # table for pressure in db
    name_rtd = ['rtd0', 'rtd1', 'rtd2', 'rtd3', 'rtd4', 'rtd5']
    types_rtd = ['FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT']
    ardpath = "/dev/ttyACM0"
    arduino = serial.Serial(ardpath)
    arduino.baudrate = 9600
    arduino.parity = 'N'
    arduino.stopbits = 1
    arduino.bytesize = 8

    sleep(0.1)

    RTD = arduino.readline().decode('utf8')
    if(RTD[3:7] == '' or convert_RTD_ADC(RTD[3:7], 0) == False):
        R0 = None
    else:
        R0 = convert_RTD_ADC(float(RTD[3:7]), 0)    # (ADC number, offset)
    #print("R0 is " + str(R0) + "K")

    if(RTD[11:15] == '' or convert_RTD_ADC(RTD[11:15], 0) == False):
        R1 = None
    else:
        R1 = convert_RTD_ADC(float(RTD[11:15]), 0)    # (ADC number, offset)
    #print("R1 is " + str(R1) + "K")

    if(RTD[19:23] == '' or convert_RTD_ADC(RTD[19:23], 0) == False):
        R2 = None
    else:
        R2 = convert_RTD_ADC(float(RTD[19:23]), 0)    # (ADC number, offset)
    #print("R2 is " + str(R2) + "K")

    if(RTD[27:31] == '' or convert_RTD_ADC(RTD[27:31], 0) == False):
        R3 = None
    else:
        R3 = convert_RTD_ADC(float(RTD[27:31]), 0)    # (ADC number, offset)
    #print("R3 is " + str(R3) + "K")

    if(RTD[35:39] == '' or convert_RTD_ADC(RTD[35:39], 0) == False):
        R4 = None
    else:
        R4 = convert_RTD_ADC(float(RTD[35:39]), -30)    # (ADC number, offset)
    #print("R4 is " + str(R4) + "K")

    if(RTD[43:47] == '' or convert_RTD_ADC(RTD[43:47], 0) == False):
        R5 = None
    else:
        R5 = convert_RTD_ADC(float(RTD[43:47]), -23)    # (ADC number, offset)
    #print("R5 is " + str(R5) + "K")

    values_rtd = [R0, R1, R2, R3, R4, R5]

    if(R0 != None and R1 != None and R2 != None and R3 != None and R4 != None and R5 != None):
        # insert
        #cursor.setup(name_rtd, types = types_rtd)
        #cursor.register(values_rtd)
        setups_name = [*name_rtd, *name_pressure]
        setups_types = [*types_rtd, *types_pressure]
        cursor.setup(setups_name, setups_types)
        cursor.register([*values_rtd, *values_pressure])
        

    return
    #except:
    #    pass
    #    return

