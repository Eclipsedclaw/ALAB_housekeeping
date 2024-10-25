# Author: Jiancheng Zeng(JC)
# Date: May 8th, 2024

import time
import pymysql
from datetime import datetime
from time import sleep
import serial
from serial.tools import list_ports
import RPi.GPIO as GPIO
import math
from lazyins import Cursor
import os
from gpiozero import LED
import ALABHK_query

print("pymysql version is: ", pymysql.__version__)
print("pymysql location at: ", pymysql.__file__)
for i in range(10):
    rtd = ALABHK_query.get_rtd()
    print("current rtd readout is: ", rtd)
    time.sleep(1)