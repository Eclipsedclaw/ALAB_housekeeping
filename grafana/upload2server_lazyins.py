#!/usr/bin/env python

import pymysql
from datetime import datetime
from time import sleep
import serial
from serial.tools import list_ports
import RPi.GPIO as GPIO
import math
from lazyins import Cursor
import os


def do_nothing(x):
    return x

# This function query compressor status and send to mysql database
def get_compressor():

    cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'LAr_TPCruns_data', table_name = 'compressor')

    # table for compressor in db
    name_compressor = ['T1', 'T2', 'T3']
    types_compressor = ['int', 'int', 'int']


    compresspath = "/dev/compress"
    Compressor = serial.Serial(compresspath)
    Compressor.baudrate = 9600
    Compressor.parity = 'N'
    Compressor.stopbits = 1
    Compressor.bytesize = 8

    Compressor.write(b'$TEAA4B9\r')
    CompressorOut = Compressor.read(Compressor.inWaiting()).decode('utf8')
    T1_temp = int(CompressorOut[6:8])
    T2_temp = int(CompressorOut[10:12])
    T3_temp = int(CompressorOut[14:16])

    sleep(0.1)

    values_compressor = [T1_temp, T2_temp, T3_temp]
    
    # insert
    cursor.setup(name_compressor, types = types_compressor)
    cursor.register(values_compressor)

    return


# This function query pressure data from the pressure gauge and send to mysql database
def get_pressure():

    cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'LAr_TPCruns_data', table_name = 'pressure')

    # table for pressure in db
    name_pressure = ['chamber_pressure', 'jacket_pressure']
    types_pressure = ['float', 'float']

    chamberpressurepath = "/dev/toppress"
    chamberPressure = serial.Serial(chamberpressurepath)
    chamberPressure.baudrate = 9600
    chamberPressure.parity = 'N'
    chamberPressure.stopbits = 1
    chamberPressure.bytesize = 8
    chamberPressure.write(('$@001PR3?;FF').encode('utf8'))
    
    sleep(0.1)

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

    # TO DO: figure out why somehow it need to sleep for a certain time to readout normally
    sleep(0.1)

    JacketPressureOut = jacketPressure.read(jacketPressure.inWaiting()).decode('utf8')
    if(JacketPressureOut[7:14] == ''):
        jacket_pressure = None
    else:
        jacket_pressure = float(JacketPressureOut[7:14])
    #print("jacket pressure is: " + str(jacket_pressure))
   
    values_pressure = [chamber_pressure, jacket_pressure]
    
    # insert
    cursor.setup(name_pressure, types = types_pressure)
    cursor.register(values_pressure)

    return

if __name__ == '__main__':

    sleep_sec = 1
    while True:
        get_pressure()
        get_compressor()
        sleep(sleep_sec)


