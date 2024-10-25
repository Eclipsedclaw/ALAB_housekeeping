import time
import math
from datetime import datetime

import serial
from serial.tools import list_ports

import smtplib as smt # For email stuff
from email.message import EmailMessage # For email stuff

import tkinter as tk
import tkinter.scrolledtext
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd

import RPi.GPIO as GPIO

from time import sleep

import pymysql
from datetime import datetime
from time import sleep
import serial
from serial.tools import list_ports
import RPi.GPIO as GPIO
import math
from lazyins import Cursor
import os

devices = [info.device for info in list_ports.comports()]
print(devices)

toppath = "/dev/ttyUSB1"

# Open the serial port
Gauge1 = serial.Serial(port=toppath, timeout=1)

print("Gauge1 is:", Gauge1)
time.sleep(1)

# Send command to the gauge
Gauge1.write(('@253PR3?;FF').encode('utf8'))
GaugeP1 = Gauge1.read(Gauge1.inWaiting()).decode('utf8')
print('Main Chamber Address:' + GaugeP1 )

#Gauge1.write(('@001BR!19200;FF').encode())
#print("Gauge1 is:", Gauge1)
#data = Gauge1.readline().decode('utf-8').strip()

# Send command to the gauge
#Gauge1.write(('@254AD?;FF').encode())

# Read data from the serial port
#data = Gauge1.readline().decode('utf-8').strip()
        
# Print the raw data received
#print("Received raw data:", data)
#time.sleep(1)




# import pyvisa as visa

# # Create a Visa resource manager
# rm = visa.ResourceManager()

# # Find the USB Keyspan serial adapter
# serial_adapters = rm.list_resources('?*::INSTR')
# print(serial_adapters)


# serial = rm.open_resource(serial_adapters[0])
# print(serial)

# # Set communication parameters
# serial.baud_rate = 9600
# serial.data_bits = 8
# serial.read_termination = '\cr'
# serial.write_termination = '\cr'

# # Read from the serial port
# try:
#     while True:
#         data_write = serial.write('$@254AD?;FFF')
#         print(data_write)
#         data = serial.read()
#         if data:
#             print("Received:", data)
# except KeyboardInterrupt:
#     # Close the serial port when Ctrl+C is pressed
#     serial.close()
#     print("\nSerial port closed.")
