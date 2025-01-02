import time
import serial
from serial.tools import list_ports

# search serial port
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)

for n in range(100):
    MKSpath = "/dev/ttyS0"
    MKS = serial.Serial(MKSpath)
    MKS.baudrate = 9600

    MKS.write(("test").encode('utf-8'))
    time.sleep(0.1)

    readout = MKS.read(MKS.inWaiting())
    print("serial output is: ", readout)

    serial_out = readout.decode('utf-8')

    print("serial output after utf-8 decode is: ",serial_out)
    time.sleep(1)


