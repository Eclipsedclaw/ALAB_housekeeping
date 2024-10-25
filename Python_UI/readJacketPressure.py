import serial
import time

Gauge = serial.Serial()
Gauge.baudrate = 9600
Gauge.parity = "N"
Gauge.stopbits = 1
Gauge.bytesize = 8
flag = 0

GaugePath = "/dev/botpress"
GaugeStat = 1

try:
    Gauge = serial.Serial(GaugePath)
except serial.SerialException or serial.serialutil.SerialException:
    GaugeStat = 0

if GaugeStat == 1:
    Gauge.write(("$@254PR3?;FF").encode("utf8"))
    time.sleep(0.6)
    ack = Gauge.read(Gauge.inWaiting()).decode("utf8")
    while (ack == None or len(ack)==0 and flag <= 10):
        print ("No response. Trying again.")
        Gauge.write(("$@254PR3?;FF").encode("utf8"))
        time.sleep(1)
        ack = Gauge.read(Gauge.inWaiting()).decode("utf8")
        flag += 1
    print (ack)
    Gauge.close()
    print ("Bye :)")
elif GaugeStat == 0:
    print ("Disconnected/port not found")
