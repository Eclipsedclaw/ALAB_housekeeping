import time
import serial

SerialObj = serial.Serial('/dev/ttyUSB0')
SerialObj.baudrate = 9600
SerialObj.parity = 'N'
SerialObj.stopbits = 1
SerialObj.bytesize = 8
time.sleep(3)

SerialObj.write(b'$ON177CF\r')

time.sleep(5)


SerialObj.write(b'$OFF9188\r')
time.sleep(1)

SerialObj.close()
