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

# Define reasonable limits for validation
MAX_DRV_CURRENT = 10.0  # Adjust this value based on your device specifications
MAX_DRV_VOLTAGE = 50.0  # Adjust this value based on your device specifications

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

        # Define all turbo parameters
        name_turbo = ['RemotePrio','SpdSwPtAtt','ErrorCode','OvTempElec','OvTempPump','SetSpdAtt','PumpAccel',
                      'SetRotSpd','ActualSpd','DrvCurrent','OpHrsPump','FwVersion', 'DrvVoltage','OpHrsElec',
                      'NominalSpd','DrvPower','PumpCylces','TempElec','TempPmpBot','AccelDecel','TempBearng',
                      'TempMotor','ElecName','HWVersion','ErrHist1','ErrHist2','ErrHist3','ErrHist4',
                      'ErrHist5','ErrHist6','ErrHist7','ErrHist8','ErrHist9','ErrHist10']
        types_turbo = ['int', 'int', 'VARCHAR(10)', 'int', 'int', 'int', 'int',
                       'int', 'int', 'DECIMAL(6,2)', 'int', 'int', 'DECIMAL(6,2)', 'int',
                       'int', 'int', 'int', 'int', 'int', 'int', 'int',
                       'int', 'VARCHAR(10)', 'int', 'VARCHAR(10)', 'VARCHAR(10)', 'VARCHAR(10)', 'VARCHAR(10)',
                       'VARCHAR(10)', 'VARCHAR(10)', 'VARCHAR(10)', 'VARCHAR(10)', 'VARCHAR(10)', 'VARCHAR(10)']
        parameters_turbo = [300, 302, 303, 304, 305, 306, 307,
                           308, 309, 310, 311, 312, 313, 314,
                           315, 316, 319, 326, 330, 336, 342,
                           346, 349, 354, 360, 361, 362, 363,
                           364, 365, 366, 367, 368, 369]

        compresspath = "/dev/ttyUSB" + device
        Compressor = serial.Serial(compresspath, baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=2)
        
        # Initialize list to store all values
        values_turbo = []
        
        # Loop through all parameters
        for i, param in enumerate(parameters_turbo):
            try:
                # Create command for each parameter
                # Format: 001: address, 00: read, XXX: parameter, 02: digits, =?: query
                base_command = f'00100{param}02=?'
                
                # Calculate checksum: sum of ASCII values modulo 256
                checksum = sum(ord(c) for c in base_command) % 256
                
                command = f'{base_command}{checksum:03d}\r'
                
                # Send command
                Compressor.write(command.encode('ascii'))
                print(f"Reading {name_turbo[i]} (param {param}): {command.strip()}")
                
                # Wait for response
                sleep(0.01)
                
                # Read response
                response = Compressor.read(20)
                print(f"Raw response: {response}")
                decoded_response = response.decode('ascii', errors='ignore')
                print(f"Decoded response: {decoded_response}")
                
                # Extract value from response (assuming same format as original)
                # You may need to adjust the slice indices [10:16] based on actual response format
                
                if param in {303, 349, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369}:  # Error Codes and the Electronic Name
                    value = decoded_response[10:16].strip()
                elif param in {310, 313}:
                    value = decoded_response[10:16].strip()
                    try:
                        # Convert to int first, then to decimal format
                        int_value = int(value)
                        decimal_value = round(int_value / 100, 2)  # Convert 123456 to 1234.56
                        # Validate DrvCurrent and DrvVoltage
                        if param == 310:  # DrvCurrent
                            if decimal_value > MAX_DRV_CURRENT:
                                print(f"ERROR: DrvCurrent value {decimal_value} exceeds maximum limit {MAX_DRV_CURRENT}. Storing NULL.")
                                value = None
                            else:
                                value = decimal_value
                        elif param == 313:  # DrvVoltage
                            if decimal_value > MAX_DRV_VOLTAGE:
                                print(f"ERROR: DrvVoltage value {decimal_value} exceeds maximum limit {MAX_DRV_VOLTAGE}. Storing NULL.")
                                value = None
                            else:
                                value = decimal_value
                    except ValueError:
                        value = None
                        print(f"Warning: Could not convert '{decoded_response[10:16]}' to int for {name_turbo[i]}")

                elif len(decoded_response) > 16 and decoded_response[10:16].strip():
                    value = decoded_response[10:16].strip()
                    try:
                        value = int(value)
                    except ValueError:
                        value = None
                        print(f"Warning: Could not convert '{decoded_response[10:16]}' to int for {name_turbo[i]}")
                else:
                    value = None
                    print(f"Warning: Empty or invalid response for {name_turbo[i]}")
                
                values_turbo.append(value)
                
                # Small delay between commands to avoid overwhelming the device
                sleep(0.01)
                
            except Exception as param_error:
                print(f"Error reading parameter {param} ({name_turbo[i]}): {param_error}")
                values_turbo.append(None)
                continue

        print("Current turbo status:", dict(zip(name_turbo, values_turbo)))

        # Insert data to mysql database
        cursor.setup(name_turbo, types=types_turbo)
        cursor.register(values_turbo)

        Compressor.close()
        return values_turbo
        
    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
        return None
    except Exception as e:
        print(f"Database or other error: {e}")
        return None

try:
    while True:
        temp_value = get_compressor()
        if temp_value:
            print("Successfully read turbo data")
        else:
            print("Failed to read turbo data")
        time.sleep(0.01)  # Increased delay since we're reading more parameters
except KeyboardInterrupt:
    print("Process interrupted by the user.")