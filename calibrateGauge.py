import serial
import time

PressureGauge = serial.Serial()
# Put desired path below
path = "/dev/toppress"
PressureGauge.baudrate = 9600
PressureGauge.parity = "N"
PressureGauge.stopbits = 1
PressureGauge.bytesize = 8
stat = 1

# Check if connected to port
try:
    PressureGauge = serial.Serial(path)
except serial.SerialException or serial.serialutil.SerialException:
    stat = 0

# Sending command to calibrate if on/connected
if stat == 1:
    PressureGauge.write(('$@253ATM!7.60E+2;FF').encode('utf8'))
    time.sleep(0.6)
    ack = PressureGauge.read(PressureGauge.inWaiting()).decode("utf8")
    print (ack)
elif stat == 0:
    print("Gauge not connected/port not open")
