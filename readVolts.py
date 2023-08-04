from pyfirmata import Arduino, util
from time import sleep
import math

# Changed the symlink for the port to arduino! No need to go guessing again. -Robin
board = Arduino('/dev/arduino')

it = util.Iterator(board)
it.start()

print("Connected.")

pins = [0, 1, 2, 3, 4, 5]

for pin in pins:
    board.analog[pin].enable_reporting()
    print ("Turned on pin %d to read." % (pin))
    sleep(1)

while True:
    for val in pins:
        board.analog[val].enable_reporting()
        print ("Turned on pin %d." % (val))
        sleep(1)
        analog_read = board.analog[val].read()
        sleep(1)
        if analog_read != None:
            print("Voltage is: %f" % (analog_read))
        elif analog_read == None:
            print("No response received.")
#while True:
#    for val in pins:
#        analog_read = board.analog[val].read()
#        if analog_read != None:
#            print("Voltage for pin %d  is: %f" % (val, analog_read*5.0/1023.0))
#        elif analog_read == None:
#            print("No response received from pin %d." % (val))
#"""
