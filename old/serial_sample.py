import serial
ser = serial.Serial(port='/dev/ttyUSB0',baudrate=9600,bytesize=8,parity='N',timeout=0)

#command = b'\x48\x65\x6c\x6c\x6f\0D'
#command = b'\x4f\x4e\x31\x37\x37\x37\x43\x46'
command = b'hello'
ser.write(command)
ser.write(command)


#cw = [0x24,0x4f,0x4e,0x31]
#ser.write(serial.to_bytes(cw))

#c2 = [0x37,0x37,0x43,0x46,0x0D]
#ser.write(serial.to_bytes(c2))
