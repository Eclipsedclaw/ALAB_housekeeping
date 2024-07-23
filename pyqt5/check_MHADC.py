import time
import serial
from serial.tools import list_ports

# search serial port
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)

def MHADC_readout(serial_path, serial_baudrate = 115200):
    while True:
        MHADCpath = serial_path
        MHADC = serial.Serial(MHADCpath)
        MHADC.baudrate = serial_baudrate
        
        readout = MHADC.readline()
        print("serial output is: ", readout)

        serial_out = readout.decode('utf-8')

        print("serial output after utf-8 decode is: ",serial_out)
        return serial_out


test_data = MHADC_readout(serial_path='/dev/ttyACM0')
print(test_data[3:7])

