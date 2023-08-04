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
port = "/dev/ttyUSB2",
baudrate = 9600,
bytesize = serial.EIGHTBITS, 
parity = serial.PARITY_NONE,
stopbits = serial.STOPBITS_ONE, 
timeout = 1,
xonxoff = False,
rtscts = False,
dsrdtr = False,
writeTimeout = 2
)



#ser.isOpen()


# search serial port
#ser = serial.Serial()
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)


print ('Enter your commands below.\r\nInsert "exit" to leave the application.')
port_in=0
data_in=0
while True :
#    port_in = int(input("select device: "))
#    port_in = input("select device (/dev/ttyUSB0) ")
    print("command ($@253PR3?;FF)?" )
    data_in = input(">> ")
#    if (data_in == 'exit' or port_in == 'exit'):
    if (data_in == 'exit'):
        ser.close()
        break
    else:
        print(data_in)
#        ser.port = devices[port_in]
#        ser.port = port_in  
#        ser.open()
        ser.write((data_in).encode('utf-8'))
        out = ''
        time.sleep(1)
        while ser.inWaiting() > 0:
           # out = ser.read(ser.inWaiting()).decode('utf8')
            out = ser.read(ser.inWaiting())
        if out != '':
            print (out)
