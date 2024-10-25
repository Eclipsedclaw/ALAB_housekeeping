import time
import serial
from serial.tools import list_ports
from lazyins import Cursor
import os
import re

def MKS_serial_command(MKS_command, serial_path, serial_baudrate = 115200, serial_parity = 'N', serial_stopbits = 1, serial_bytesize = 8):
    while True:
        MKSpath = serial_path
        MKS = serial.Serial(MKSpath)
        MKS.baudrate = serial_baudrate
        MKS.parity = serial_parity
        MKS.stopbits = serial_stopbits
        MKS.bytesize = serial_bytesize

        print("You are sending command: ", MKS_command, " to device: ", serial_path)
        MKS.write((MKS_command).encode('utf-8'))
        time.sleep(0.1)
        
        readout = MKS.read(MKS.inWaiting())
        print("serial output is: ", readout)

        serial_out = readout.decode('utf-8')

        print("serial output after utf-8 decode is: ",serial_out)
        return serial_out
    #except Exception as e:
    #    print("Error in MKS serial communication:", e)
    #    return None

def pump_data(serial_path, serial_baudrate = 115200, serial_parity = 'N', serial_stopbits = 1, serial_bytesize = 8):
    while True:
        MKSpath = serial_path
        MKS = serial.Serial(MKSpath)
        MKS.baudrate = serial_baudrate
        MKS.parity = serial_parity
        MKS.stopbits = serial_stopbits
        MKS.bytesize = serial_bytesize

        print("Getting pressure data now...")
        #host=os.environ.get('LAZYINS_HOST')
        #print("host is: "+str(host))

        try:
            cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'bench_test', table_name = 'MKS_gauge')
            
            # table for pressure in db
            name_pressure = ['PR1', 'PR2', 'PR3', 'PR4', 'PR5']
            types_pressure = ['float', 'float', 'float', 'float', 'float']
            chamber_pressure = []
            for i in range(5):
                command = "@002PR"+str(i+1)+"?;FF"
                MKS.write((command).encode('utf8'))
                time.sleep(0.1)
                try:
                    ChamberPressureOut = MKS.read(MKS.inWaiting()).decode('utf8')
                    print("ChamberPressureOut for PR"+str(i+1)+" string is: "+ str(ChamberPressureOut))
                    match = re.search(r'@002ACK(.*?)\;FF', ChamberPressureOut)
                    chamber_pressure.append(abs(float(match.group(1))))
                except Exception as e:
                    print("Error in chamber pressure query:", e)
                finally:
                    print("")
                time.sleep(0.1)

            # Ensure the port is closed properly
            MKS.close()
            values_pressure = chamber_pressure

            # insert
            cursor.setup(name_pressure, types = types_pressure)
            cursor.register(values_pressure)

            print("Current pressure: ", values_pressure)
            return values_pressure
        except Exception as e:
            print("Error in pressure query:", e)
            pass
            return None


MKS_serial_command(MKS_command='@002GT!AIR;FF', serial_path='/dev/ttyUSB0')

#pump_data(MKS_command='@002PR3?;FF', serial_path='/dev/cu.usbserial-0001')

try:
    while True:
        pump_data(serial_path='/dev/ttyUSB0')
        time.sleep(0.1)  # Delay for 0.1 second
except KeyboardInterrupt:
    print("Process interrupted by the user.")
