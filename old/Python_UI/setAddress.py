import serial
import time

Gauge = serial.Serial()
Gauge.baudrate = 9600
Gauge.parity = "N"
Gauge.stopbits = 1
Gauge.bytesize = 8
# Enter your device path here
GaugePath = "/dev/toppress"
GaugeStat = 1

try:
    Gauge = serial.Serial(GaugePath)
except serial.SerialException or serial.serialutil.SerialException:
    GaugeStat = 0

if GaugeStat == 1:
    time.sleep(0.6)
    Gauge.write(("$@001AD?;FF").encode("utf8"))
    time.sleep(0.6)
    ack = Gauge.read(Gauge.inWaiting()).decode("utf8")
    while (ack == None or len(ack)==0):
        print("No response. Trying again.")
        Gauge.write(("$@001AD?;FF").encode("utf8"))
        time.sleep(1)
        ack = Gauge.read(Gauge.inWaiting()).decode("utf8")
        print (ack)
	#print(Gauge.read(Gauge.inWaiting()))
    if ack == None or len(ack)==0:
        print("No response.")
    elif ack != None:
        print (ack)
elif GaugeStat == 0:
    print("Disconnected/port not found")
"""
if GaugeStat == 1:
    print (Gauge.isOpen())
    Gauge.write(("$@254TST!ON;FF").encode("utf8"))
    time.sleep(0.6)
    ack = Gauge.read(Gauge.inWaiting()).decode("utf8")
    print (ack)
elif GaugeStat == 0:
    print ("Disconnected/port not found")
Gauge.close()
print("Done")
"""
