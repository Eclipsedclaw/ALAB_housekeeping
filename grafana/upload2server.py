#!/usr/bin/env python

import pymysql
from datetime import datetime
from time import sleep
import serial
from serial.tools import list_ports
import RPi.GPIO as GPIO
import math


def do_nothing(x):
    return x

def unix_timestamp(i):
    return datetime.fromtimestamp(i).strftime("%Y-%m-%d %H:%M:%S.%u")

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

# This is for connecting to mysql database
def connect_table():

    config = {
            "login":{
                    "host": "192.168.1.242",
                            "port": 3306, "user": "root",
                            "passwd": "darkmatter",
                            "autocommit": True
                    },
                    "name": "LAr_TPCruns_data"
             }

    conn = pymysql.connect(**config['login'])
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("CREATE DATABASE IF NOT EXISTS " + config['name'])
    cursor.execute("USE " + config['name'])
    return cursor

# This function query compressor status and send to mysql database
def get_compressor():

    cursor = connect_table()
    # Make table if needed for compressor
    table_query = 'CREATE TABLE IF NOT EXISTS compressor (id int auto_increment, time TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP ,'
    column_names = ['T1', 'T2', 'T3']
    column_types = ['int','int','int']
    for n, t in zip(column_names, column_types):
        table_query += ' {} {},'.format(n, t)
    table_query += ' PRIMARY KEY (id));'
    cursor.execute(table_query)

    compresspath = "/dev/compress"
    Compressor = serial.Serial(compresspath)
    Compressor.baudrate = 9600
    Compressor.parity = 'N'
    Compressor.stopbits = 1
    Compressor.bytesize = 8

    Compressor.write(b'$TEAA4B9\r')
    CompressorOut = Compressor.read(Compressor.inWaiting()).decode('utf8')
    T1_temp = CompressorOut[6:8]
    T2_temp = CompressorOut[10:12]
    T3_temp = CompressorOut[14:16]


    # insert
    insert_query = "INSERT INTO compressor (T1, T2, T3) VALUES (%s, %s, %s);"
    try:
        cursor.execute(insert_query,tuple([T1_temp, T2_temp, T3_temp]))
    except:
        pass

    return

# This function query pressure data from the pressure gauge and send to mysql database
def get_pressure():

    cursor = connect_table()
    # Make table if needed for compressor
    table_query = 'CREATE TABLE IF NOT EXISTS pressure (id int auto_increment, time TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP ,'
    column_names = ['chamber_pressure', 'jacket_pressure']
    column_types = ['FLOAT', 'FLOAT']
    for n, t in zip(column_names, column_types):
        table_query += ' {} {},'.format(n, t)
    table_query += ' PRIMARY KEY (id));'
    cursor.execute(table_query)

    chamberpressurepath = "/dev/toppress"
    chamberPressure = serial.Serial(chamberpressurepath)
    chamberPressure.baudrate = 9600
    chamberPressure.parity = 'N'
    chamberPressure.stopbits = 1
    chamberPressure.bytesize = 8
    chamberPressure.write(('$@001PR3?;FF').encode('utf8'))

    ChamberPressureOut = chamberPressure.read(chamberPressure.inWaiting()).decode('utf8')
    if(ChamberPressureOut[7:14] == ''):
        chamber_pressure = None
    else:
        chamber_pressure = float(ChamberPressureOut[7:14])
    #print("chamber pressure is: " + str(chamber_pressure))
    #print(type(chamber_pressure))

    jacketpressurepath = "/dev/botpress"
    jacketPressure = serial.Serial(jacketpressurepath)
    jacketPressure.baudrate = 9600
    jacketPressure.parity = 'N'
    jacketPressure.stopbits = 1
    jacketPressure.bytesize = 8
    jacketPressure.write(('$@253PR3?;FF').encode('utf8'))

    JacketPressureOut = jacketPressure.read(jacketPressure.inWaiting()).decode('utf8')
    if(JacketPressureOut[7:14] == ''):
        jacket_pressure = None
    else:
        jacket_pressure = float(JacketPressureOut[7:14])
    #print("jacket pressure is: " + str(jacket_pressure))

    # insert
    insert_query = "INSERT INTO pressure (chamber_pressure, jacket_pressure) VALUES (%s, %s);"
    try:
        cursor.execute(insert_query,tuple([chamber_pressure, jacket_pressure]))
    except:
        pass

    return

# This function query rtd readout from arduino and send to mysql database
def get_rtd():
    cursor = connect_table()
    # Make table if needed for arduino's rtd sensors
    table_query = 'CREATE TABLE IF NOT EXISTS rtd (id int auto_increment, time TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP ,'
    column_names = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5']
    column_types = ['FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT']
    for n, t in zip(column_names, column_types):
        table_query += ' {} {},'.format(n, t)
    table_query += ' PRIMARY KEY (id));'
    cursor.execute(table_query)

    ardpath = "/dev/arduino"
    arduino = serial.Serial(ardpath)
    arduino.baudrate = 9600
    arduino.parity = 'N'
    arduino.stopbits = 1
    arduino.bytesize = 8

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


    # insert
    insert_query = "INSERT INTO rtd (R0, R1, R2, R3, R4, R5) VALUES (%s, %s, %s, %s, %s, %s);"
    try:
        cursor.execute(insert_query, tuple([R0, R1, R2, R3, R4, R5]))
    except:
        pass

    return

if __name__ == '__main__':

    sleep_sec = 1

    while True:
        get_compressor()
        get_pressure()
        get_rtd()
        sleep(sleep_sec)


