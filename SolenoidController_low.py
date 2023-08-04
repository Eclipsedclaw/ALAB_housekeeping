import sys
import time
import RPi.GPIO as GPIO
from time import sleep 

channel = 3

GPIO.setmode(GPIO.BCM)
sleep(0.5) 
#GPIO.setmode(GPIO.BOARD)
GPIO.setup(channel, GPIO.OUT)
sleep(0.5) 
GPIO.output(channel, 0)
sleep(0.5) 
GPIO.cleanup()
