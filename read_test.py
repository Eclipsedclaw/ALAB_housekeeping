#!/usr/bin/env python

import pymysql
from datetime import datetime
from time import sleep
import serial
from serial.tools import list_ports
import RPi.GPIO as GPIO
    
    
def do_nothing(x):
    return x

def unix_timestamp(i):
    return datetime.fromtimestamp(i).strftime("%Y-%m-%d %H:%M:%S.%u")

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
    sleep(1)
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

def get_pressure():
    
    cursor = connect_table()
    # Make table if needed for compressor
    table_query = 'CREATE TABLE IF NOT EXISTS pressure (id int auto_increment, time TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP ,'
    column_names = ['chamber_pressure', 'jacket_pressure']
    column_types = ['int', 'int']
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
    
    jacketpressurepath = "/dev/botpress"
    jacketPressure = serial.Serial(jacketpressurepath)
    jacketPressure.baudrate = 9600
    jacketPressure.parity = 'N'
    jacketPressure.stopbits = 1
    jacketPressure.bytesize = 8
    jacketPressure.write(('$@253PR3?;FF').encode('utf8'))

    sleep(1)

    ChamberPressureOut = chamberPressure.read(chamberPressure.inWaiting()).decode('utf8')
    chamber_pressure = str(ChamberPressureOut[7:14])
    print(chamber_pressure)
    
    JacketPressureOut = jacketPressure.read(jacketPressure.inWaiting()).decode('utf8')
    jacket_pressure = JacketPressureOut[7:14]
    if(jacket_pressure == 0):
        jacket_pressure == NULL
    # insert
    insert_query = "INSERT INTO pressure (chamber_pressure, jacket_pressure) VALUES (%s, %s);"
    try:
        cursor.execute(insert_query,tuple([chamber_pressure, jacket_pressure]))
    except:
        pass

    return

if __name__ == '__main__':

    sleep_sec = 1

    while True:
        #get_compressor()
        get_pressure()
        sleep(sleep_sec)


#import serial
#from time import sleep

#compresspath = "/dev/compress"
#Compressor = serial.Serial(compresspath)
#Compressor.baudrate = 9600
#Compressor.parity = 'N'
#Compressor.stopbits = 1
#Compressor.bytesize = 8

#while True:
#	Compressor.write(b'$TEAA4B9\r')
#	sleep(1.2)
#	CompressorOut = Compressor.read(Compressor.inWaiting()).decode('utf8')
#    T1_temp = CompressorOut[6:8]
#    T2_temp = CompressorOUT[10:12]
#    T3_temp = CompressorOUT[14:16]

#	print(CompressorOut)
#	print(len(CompressorOut))
