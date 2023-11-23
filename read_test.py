#!/usr/bin/env python

import pymysql
from datetime import datetime
from time import sleep
import serial


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


def get_record():

    cursor = connect_table()
    # Make table if needed
    table_query = 'CREATE TABLE IF NOT EXISTS dummy_table (id int auto_increment, time TIMESTAMP not null DEFAULT CURRENT_TIMESTAMP ,'
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
    sleep(1.2)
    CompressorOut = Compressor.read(Compressor.inWaiting()).decode('utf8')
    T1_temp = CompressorOut[6:8]
    T2_temp = CompressorOut[10:12]
    T3_temp = CompressorOut[14:16]

    
    # insert
    insert_query = "INSERT INTO dummy_table (T1, T2, T3) VALUES (%s, %s, %s);" 
    try:
        cursor.execute(insert_query,tuple([T1_temp, T2_temp, T3_temp]))
    except:
        pass

    return


if __name__ == '__main__':

    sleep_sec = 1

    while True:
        get_record()
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
