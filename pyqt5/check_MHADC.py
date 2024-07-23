import time
import serial
from serial.tools import list_ports
from ALABHK_query import convert_RTD_ADC

# search serial port
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)

def test_MHADC(serial_path, serial_baudrate = 115200):
    while True:
        MHADCpath = serial_path
        MHADC = serial.Serial(MHADCpath)
        MHADC.baudrate = serial_baudrate
        
        readout = MHADC.readline()
        print("serial output is: ", readout)

        serial_out = readout.decode('utf-8')

        print("serial output after utf-8 decode is: ",serial_out)
        return serial_out


test_data = test_MHADC(serial_path='/dev/ttyACM0')
print(test_data[11:15])
print(convert_RTD_ADC(test_data[11:15], bits=12, offset=0))


if(len(test_data)==135):
            if(test_data[3:7] == '' or convert_RTD_ADC(test_data[3:7], bits=12, offset=0) == False):
                R0 = None
            else:
                R0 = convert_RTD_ADC(float(test_data[3:7]), bits=12, offset=-1)    # (ADC number, offset)
            #print("R0 is " + str(R0) + "K")

            if(test_data[11:15] == '' or convert_RTD_ADC(test_data[11:15], bits=12, offset=0) == False):
                R1 = None
            else:
                R1 = convert_RTD_ADC(float(test_data[11:15]), bits=12, offset=-1)    # (ADC number, offset)
            #print("R1 is " + str(R1) + "K")

            if(test_data[19:23] == '' or convert_RTD_ADC(test_data[19:23], bits=12, offset=0) == False):
                R2 = None
            else:
                R2 = convert_RTD_ADC(float(test_data[19:23]), bits=12, offset=-2)    # (ADC number, offset)
            #print("R2 is " + str(R2) + "K")

            if(test_data[27:31] == '' or convert_RTD_ADC(test_data[27:31], bits=12, offset=0) == False):
                R3 = None
            else:
                R3 = convert_RTD_ADC(float(test_data[27:31]), bits=12, offset=-2)    # (ADC number, offset)
            #print("R3 is " + str(R3) + "K")

            if(test_data[35:39] == '' or convert_RTD_ADC(test_data[35:39], bits=12, offset=0) == False):
                R4 = None
            else:
                R4 = convert_RTD_ADC(float(test_data[35:39]), bits=12, offset=-3)    # (ADC number, offset)
            #print("R4 is " + str(R4) + "K")

            if(test_data[43:47] == '' or convert_RTD_ADC(test_data[43:47], bits=12, offset=0) == False):
                R5 = None
            else:
                R5 = convert_RTD_ADC(float(test_data[43:47]), bits=12, offset=2)    # (ADC number, offset)
            #print("R5 is " + str(R5) + "K")

            values_MHADC = [R0, R1, R2, R3, R4, R5]

print("Temperature is: ", values_MHADC, "K")

