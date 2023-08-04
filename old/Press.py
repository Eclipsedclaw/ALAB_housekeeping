import serial
import time

port = serial.Serial('/dev/ttyUSB0', baudrate=9600,timeout=3.0)

port.write(b'@253PR1?;FF')

#time.sleep(2)

data = port.read()

print(data)

#port.close()
