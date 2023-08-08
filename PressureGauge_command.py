import time
import serial

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='/dev/botpress',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout = 1,
    xonxoff = False,
    rtscts = False,
    dsrdtr = False,
)

print(ser.name)

#ser.isOpen()

print ('Enter your commands below.\r\nInsert "exit" to leave the application.')

data_in=0
out = ''
while True:
    data_in = input(">> ")
    if data_in == 'exit':
        ser.close()
        break
    else:
        while out == '' or out == '@253NAK160;FF' or out == '@253NAK;FF':
            ser.write(('$@253PR3?;FF').encode("utf-8"))
            time.sleep(1)
            while ser.inWaiting() > 0:
                out = ser.read(ser.inWaiting()).decode("utf8")
                print (out)
        #if out != '':
         #   print (out)
