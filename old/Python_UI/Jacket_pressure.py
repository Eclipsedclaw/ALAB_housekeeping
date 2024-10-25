import time
import serial
from serial.tools import list_ports

# configure the serial connections (the parameters differs on the device you are connecting to)
#ser = serial.Serial(
#    port='/dev/ttyUSB2',
#    baudrate=9600,
#    parity='N',
#    stopbits=1,
#    bytesize=8
#)

ser = serial.Serial(
port = "/dev/botpress",
baudrate = 9600,
bytesize = serial.EIGHTBITS, 
parity = serial.PARITY_NONE,
stopbits = serial.STOPBITS_ONE, 
timeout = 1,
xonxoff = False,
rtscts = False,
dsrdtr = False,
)

out = ''


while True: 
    while out == '' or out == '@253NAK160;FF' or out == '@253NAK;FF':
        data_in = '$@253PR3?;FF'
        ser.write((data_in).encode('utf-8'))
        time.sleep(1)
        while ser.inWaiting() > 0:
            out = ser.read(ser.inWaiting()).decode('utf8')

    print(out)
    time.sleep(1)
    out = ''
