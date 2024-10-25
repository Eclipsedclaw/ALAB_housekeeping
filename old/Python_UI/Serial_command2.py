import time
import serial
from serial.tools import list_ports


# search serial port
ser = serial.Serial()
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)


# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='/dev/botpress',
    baudrate=9600,
    parity='N',
    stopbits=1,
    bytesize=8
)

print(ser.name)

#ser.isOpen()

print ('Enter your commands below.\r\nInsert "exit" to leave the application.')

data_in=0
port_in = input("type serial port name (/dev/ttyUSB0 for P1, /dev/ttyUSB2 for P2)? ")
if (port_in == 'exit'):
    ser.close()
else:
    ser.port = port_in  

    while True :
        data_in = input("type command ($@253PR3?;FF,@253MD?;FF)? ")
        if data_in == 'exit':
            ser.close()
            break
        else:
            ser.write((data_in).encode('utf-8'))
            out = ''
            time.sleep(1)
            while ser.inWaiting() > 0:
                out = ser.read(ser.inWaiting()).decode('utf8')
            if out != '':
                print (out)
