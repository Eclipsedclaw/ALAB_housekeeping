from pyfirmata import Arduino, util
from time import sleep
import math


board = Arduino('/dev/arduino')


#readings_0 = []
#index =0
#total_0 =0

it = util.Iterator(board)
it.start()

pins = (0, 1, 2, 3, 4)
for pin in pins:
    board.analog[pin].enable_reporting()
    sleep(1)
#pin = int(0)
#board.analog[pin].enable_reporting()
#sleep(1)



while True:
    for pin in pins:
        reading = board.analog[pin].read()
        print (pin)
        sleep(1)
        if reading == None: print ('None')
        else:
            V0 = float(reading)*(5.0/1023.0)
            R0 = V0*1000./(5.0-V0)
            T0 = -(math.sqrt(17.59246-0.00232*R0)-3.908)/0.00116
            print (T0)
board.exit()

#    readings_0 = board.analog[pin].read()
#    sleep(1)
#    if readings_0 == None: continue
#    else:
#        V0 = readings_0 *(5.0/1023.0)
#        R0 = V0*1000./(5.0-V0)
#        T_0 = -(math.sqrt(17.59246-0.00232*R0)-3.908)/0.00116
#        print (readings_0)
#        print (V0) 
#        print (T_0)
#        sleep(1)

