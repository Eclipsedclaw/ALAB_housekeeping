import time
import serial

# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='/dev/compress',
    baudrate=9600,
    parity='N',
    stopbits=1,
    bytesize=8
)

print(ser.name)

#ser.isOpen()

print ('Enter your commands below.\r\nInsert "exit" to leave the application.')

data_in=0
while True :
    data_in = input(">> ")
    if data_in == 'exit':
        ser.close()
        break
    else:
        ser.write((data_in+'\r').encode('utf-8'))
        out = ''
        time.sleep(1)
        while ser.inWaiting() > 0:
            out = ser.read(ser.inWaiting()).decode('utf8')
        if out != '':
            print (out)
