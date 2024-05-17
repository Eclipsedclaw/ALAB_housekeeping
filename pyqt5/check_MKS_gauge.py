import time
import serial
from serial.tools import list_ports

# search serial port
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)

def MKS_serial_command(MKS_command, serial_path):
    while True:
        # Fixed pressure gauge value, configured by Robin
        MKSpath = serial_path
        MKS = serial.Serial(MKSpath)
        MKS.baudrate = 9600
        MKS.parity = 'N'
        MKS.stopbits = 1
        MKS.bytesize = 8

        print("You are sending command: ", MKS_command, " to device: ", serial_path)
        MKS.write((MKS_command).encode('utf-8'))
        time.sleep(0.1)
        
        print("serial output is: ",MKS.read(MKS.inWaiting()))

        serial_out = MKS.read(MKS.inWaiting()).decode('utf-8')

        print("serial output after utf-8 decode is: ",serial_out)
        return serial_out
    #except Exception as e:
    #    print("Error in MKS serial communication:", e)
    #    return None


MKS_serial_command(MKS_command='@254AD?;FF', serial_path='/dev/toppress')

