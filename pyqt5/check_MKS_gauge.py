import time
import serial
from serial.tools import list_ports

# search serial port
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)

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


MKS_serial_command(MKS_command='@254AD?;FF', serial_path='/dev/ttyUSB0')

