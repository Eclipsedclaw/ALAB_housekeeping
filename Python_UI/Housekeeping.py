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

# GPIO setting
GPIO.setmode(GPIO.BCM)
V1 = 'closed'
V2 = 'closed'
V1Channel = 2
V2Channel = 2
GPIO.setup(V1Channel,GPIO.OUT)
GPIO.setup(V2Channel,GPIO.OUT)

# Heater setting
HeaterCtrl = 23
GPIO.setup(HeaterCtrl,GPIO.OUT)
#GPIO.output(HeaterCtrl, GPIO.HIGH) settings moved to second popup window

# search serial port
ser = serial.Serial()
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)

#fig = plt.figure()
fig = plt.figure(figsize=(8,3))
#plt.rcParams["font.size"] = 14
#plt.grid()
ax1 = fig.add_subplot(1, 2, 1)
ax1.set_title("Temperature [K]")
ax1.set_xlabel("Time [s]")
ax1.set_ylabel("Temperature [K]")
ax2 = fig.add_subplot(1, 2, 2)
ax2.set_title("Pressure [Torr]")
ax2.set_xlabel("Time [s]")
ax2.set_ylabel("Pressure [Torr]")

#File name
start = datetime.now()
date_time = start.strftime("%Y_%m_%d %H_%M_%S")
format_str = date_time + ".csv"

# Plot + array creation
plt.subplots_adjust(wspace=0.3)
T1,T2,T3,P1,P2,X,LT = [],[],[],[],[],[],[]
L0,L1,L2,L3,L4,L5 = [],[],[],[],[],[]
start_time = time.perf_counter()
now = datetime.now()


Compressor = serial.Serial()
compresspath = "/dev/compress"
Compressor.baudrate = 9600
Compressor.parity = 'N'
Compressor.stopbits = 1
Compressor.bytesize = 8

Gauge1 = serial.Serial()
toppath = "/dev/toppress"
Gauge1.baudrate = 9600
Gauge1.parity = 'N'
Gauge1.stopbits = 1
Gauge1.bytesize = 8
#Gauge1.write(('$@001AD?;FF').encode('utf8'))
#Gauge1.write(('$@253AD!001;FF').encode('utf8'))

Gauge2 = serial.Serial()
botpath = "/dev/botpress"
Gauge2.baudrate = 9600
Gauge2.parity = 'N'
Gauge2.stopbits = 1
Gauge2.bytesize = 8
#Gauge2.write(('$@253AD!002;FF').encode('utf8'))

LiquidLevel = serial.Serial()
ardpath = "/dev/arduino"
LiquidLevel.baudrate = 9600
LiquidLevel.parity = 'N'
LiquidLevel.stopbits = 1
LiquidLevel.bytesize = 8

Error = 0
T_sleep = 0.1 #sleep time

# Time start for showing live times for all sensors
master_start = datetime.now()

# Time control for email notification
timesince = 0
toglow = 0 # if toglow = 1, an email will be sent once toppress < 1500.0. Then toglow will be set to 0 again.

# Flags for port status and save mode
compstat = 1
topstat = 1
botstat = 1
LLstat = 1
filestat = "w"

# Initializing email variables
server = "smtp.gmail.com"
port = 587
gmail_username = "gramsuser@gmail.com"
gmail_pass = "rydqzoykdkdelgke"

# Defining a class for an email object.
class Mailer:
    def sendmail(self, toppress, flag, limit):
        to = ["suraj.a@northeastern.edu", "j.leyva@northeastern.edu", "wessling-resnick.t@northeastern.edu" \
              "zeng.jia@northeastern.edu", "t.aramaki@northeastern.edu", "n.poudyal@northeastern.edu"]

        session = smt.SMTP(server, port)
        session.ehlo()
        session.starttls()
        session.ehlo()

        message_high = "ALERT: The pressure in the main chamber is %02f torr." % toppress
        message_low = "NOTICE: The pressure is now %02f torr, which is below the threshold of %02f torr." % (toppress, limit)
        msg = EmailMessage()

        session.login(gmail_username, gmail_pass)
        msg["From"] = "gramsuser@gmail.com"
        msg["To"] = ",".join(to)

        if flag == "H":
            msg["Subject"] = "Pressure high alert"
            msg.set_content(message_high)
            session.sendmail(gmail_username, to, msg.as_string())
        elif flag == "L":
            msg["Subject"] = "Normal pressure level restored"
            msg.set_content(message_low)
            session.sendmail(gmail_username, to, msg.as_string())
        session.quit()

def format_time(timedelta_obj):
    tot_sec = timedelta_obj.total_seconds()
    days = tot_sec // 86400
    sec_wo_days = tot_sec - (days*86400)
    hours = sec_wo_days // 3600
    sec_wo_hours = sec_wo_days - (hours*3600)
    mins = sec_wo_hours // 60
    sec_wo_mins = sec_wo_hours - (mins*60)
    sec = sec_wo_mins
    return("%02d:%02d:%02d:%02d" % (days, hours, mins, sec))

def loop():
    global Compressor,Gauge1,Gauge2,flg,Error,V1,V2
    global compstat, topstat, botstat, LLstat
    global timesince, toglow
    #Compressor: /dev/ttyUSB2
#    print (cbCompressor.get())
    try:
        Compressor = serial.Serial(compresspath)
    except serial.SerialException or serial.serialutil.SerialException:
        compstat = 0

# Compressor.port = cbCompressor.get()
#    Compressor.baudrate = 9600
#    Compressor.parity = 'N'
#    Compressor.stopbits = 1
#    Compressor.bytesize = 8
#    Compressor.timeout = T_sleep

    #Pressure Gauge1: /dev/ttyUSB0
#    print (cbPG1.get())
    try:
       Gauge1 = serial.Serial(toppath)
    except serial.SerialException or serial.serialutil.SerialException:
        topstat = 0
#    Gauge1.port = cbPG1.get()
#    Gauge1.baudrate = 9600
#    Gauge1.parity = 'N'
#    Gauge1.stopbits = 1
#    Gauge1.bytesize = 8
#    Gauge1.timeout = T_sleep

    #Pressure Gauge2: /dev/ttyUSB1
#    print (cbPG2.get())
    # This is the bottom pressure gauge
    try:
        Gauge2 = serial.Serial(botpath)
    except serial.SerialException or serial.serialutil.SerialException:
        botstat = 0
#    Gauge2.port = cbPG2.get()
#    Gauge2.baudrate = 9600
#    Gauge2.parity = 'N'
#    Gauge2.stopbits = 1
#    Gauge2.bytesize = 8
#    Gauge2.timeout = T_sleep

    #Liquid Level Sensor: /dev/ttyACM0 # Now permanently at /dev/arduino. - Robin
    try:
        LiquidLevel = serial.Serial(ardpath)
    except serial.SerialException or serial.serialutil.SerialException:
        LLstat = 0

    print(topstat, botstat, compstat, LLstat)
    print('start the program')
    while True:
        if flg == False:
            print('stop the program')
            flg = True
            break
        else:
            if compstat == 1:
                # Compressor temperature
                Compressor.write(b'$TEAA4B9\r')
                time.sleep(T_sleep)
                CompressorOut = Compressor.read(Compressor.inWaiting()).decode('utf8')
                flag1 = 0
                
                #grafana setup
                # Keita's module for eazy sql input
                print("host is: " + str(os.environ.get('LAZYINS_HOST')))
                cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'LAr_TPCruns_data', table_name = 'compressor')
                
                # table for compressor in db, currently shows compressor temperature T1/T2/T3
                name_compressor = ['T1', 'T2', 'T3']
                types_compressor = ['int', 'int', 'int']

                # Todo: figure out why it need to sleep for a certain amount of time
                sleep(1)

                # This is to check whether there is any values properly read
                if(CompressorOut[6:8] == ''):
                    T1_temp = None
                else:
                    T1_temp = CompressorOut[6:8]
                if(CompressorOut[10:12] == ''):
                    T2_temp = None
                else:
                    T2_temp = CompressorOut[10:12]
                if(CompressorOut[14:16] == ''):
                    T3_temp = None
                else:
                    T3_temp = CompressorOut[14:16]

                values_compressor = [T1_temp, T2_temp, T3_temp]

                # insert data to mysql database
                cursor.setup(name_compressor, types = types_compressor)
                cursor.register(values_compressor)
        
                while (len(CompressorOut) != 26 and flag1 <= 3):
                    print ('Compressor temperature readout error')
                    Compressor.write(b'$TEAA4B9\r')
                    time.sleep(T_sleep)
                    CompressorOut = Compressor.read(Compressor.inWaiting()).decode('utf8')
                    flag1 += 1
                #$TEA,021,015,015,000,6F37
                print (CompressorOut)
                if len(CompressorOut) == 26:
                    comp_time = datetime.now()
                    comp_delta = comp_time - master_start
                    entCompressor.delete(0, tkinter.END)
                    entCompressor.insert(tkinter.END, format_time(comp_delta))
    #            print (len(CompressorOut))
                    T1_tmp = float(CompressorOut[6:8])
                    txtT1.delete(0,tkinter.END)
                    if T1_tmp >= 90.0:
                        txtT1.config(bg="#e05a5a", fg="black")
                        txtT1.insert(tkinter.END,T1_tmp)
                    elif T1_tmp <= 89.9:
                        txtT1.config(bg="#5ae084", fg = "black")
                        txtT1.insert(tkinter.END, T1_tmp)
                    T2_tmp = float(CompressorOut[10:12])
                    txtT2.delete(0,tkinter.END)
                    if T2_tmp >= 90.0:
                        txtT2.config(bg="#e05a5a", fg="black")
                        txtT2.insert(tkinter.END,T2_tmp)
                    elif T2_tmp <= 89.9:
                        txtT2.config(bg="#5ae084", fg="black")
                        txtT2.insert(tkinter.END, T2_tmp)
                    T3_tmp = float(CompressorOut[14:16])
                    txtT3.delete(0,tkinter.END)
                    if T3_tmp >= 90.0:
                        txtT3.config(bg="#e05a5a", fg="black")
                        txtT3.insert(tkinter.END,T3_tmp)
                    elif T3_tmp <= 89.9:
                        txtT3.config(bg="#5ae084", fg="black")
                        txtT3.insert(tkinter.END,T3_tmp)
    #            print (T1_tmp,T2_tmp,T3_tmp)
                elif len(CompressorOut) != 26:
                    T1_tmp = None
                    T2_tmp = None
                    T3_tmp = None
                # Compressor status
                Compressor.write(b'$STA3504\r')
                time.sleep(T_sleep)
                CompressorOut = Compressor.read(Compressor.inWaiting()).decode('utf8')
                flag2 = 0
                while (len(CompressorOut) != 15 and flag2 <= 3):
                    print ('Compressor status readout error')
                    Compressor.write(b'$STA3504\r')
                    time.sleep(T_sleep)
                    CompressorOut = Compressor.read(Compressor.inWaiting()).decode('utf8')
                    flag2 += 1
                #$STA,0000,FAD0
                print (CompressorOut)
    #            print (len(CompressorOut))
                if len(CompressorOut) == 15:
                    Status_tmp = CompressorOut[5:9]
                    if(Status_tmp == '0000' and Error == 0): Status = 'OFF'
                    elif(Status_tmp == '0301'and Error == 0): Status = 'OK'
                    else:
                        Status = 'ERROR'
                        Error = 1
                    txtStatus.delete(0,tkinter.END)
                    txtStatus.insert(tkinter.END,Status)
                elif len(CompressorOut) != 15:
                    Status_tmp = None
            elif compstat == 0:
                print("Compressor port not found/open")
                T1_tmp = None
                T2_tmp = None
                T3_tmp = None
                Status_tmp = None
#            print (Status_tmp)

            cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'LAr_TPCruns_data', table_name = 'pressure')
            # table for pressure in db
            name_pressure = ['chamber_pressure', 'jacket_pressure']
            types_pressure = ['float', 'float']
            if topstat == 1:
                # Pressure gauge 1
#               This part is for querying the address of the sensor. Uncomment if you want to display that! 
                Gauge1.write(('$@253AD!001;FF').encode('utf8'))
                #Gauge1.write(('$@254AD?;FF').encode('utf8'))
                #time.sleep(5*T_sleep)
                #GaugeP1 = Gauge1.read(Gauge1.inWaiting()).decode('utf8')
                #print('Main Chamber Address:' + GaugeP1 )

                #Gauge1.write(('$@253AD!001;FF').encode('utf8'))
                time.sleep(T_sleep)
                Gauge1.write(('$@001PR3?;FF').encode('utf8'))
                #Gauge1.write(('@253PR3?;FF').encode('utf8'))
#               Gauge.write(b'$@253PR4?;FF')
                time.sleep(2*T_sleep)
                GaugeP1 = Gauge1.read(Gauge1.inWaiting()).decode('utf8')
#                print('Main Chamber:' + GaugeP1 + " ;len = " +str(len(GaugeP1)))

                flag3 = 0
                while (len(GaugeP1) != 17 and flag3 <= 3):
                    try:
                        print ('Pressure gauge (P1) readout error')
                        Gauge1.write(('$@001PR3?;FF').encode('utf8'))
                        time.sleep(T_sleep)
                        GaugeP1 = Gauge1.read(Gauge1.inWaiting()).decode('utf8')
 #                       print(GaugeP1 + " ;len = " +str(len(GaugeP1)))
                    except UnicodeDecodeError:
                        print ("Event lost")
                        pass
                    flag3 += 1
                #@253ACK6.41E+2;FF
                if len(GaugeP1) == 17:
                    top_time = datetime.now()
                    top_delta = top_time - master_start
                    entPG1.delete(0, tkinter.END)
                    entPG1.insert(tkinter.END, format_time(top_delta))
    #            print (len(GaugeP1))
                    P1_tmp = float(GaugeP1[7:14])
    #            P1_tmp = GaugeOut[7:15]
                    txtP1.delete(0,tkinter.END)
              #  if P1_tmp >= 90.0:
                    txtP1.insert(tkinter.END,P1_tmp)
                    # Email stuff start
                    timenow = time.perf_counter()
                    P1_lim = 1300.0
                    if (P1_tmp > P1_lim  and timenow - timesince > 3600.0):
                        alert = Mailer()
                        alert.sendmail(P1_tmp, "H", P1_lim)
                        toglow = 1
                        timesince = time.perf_counter()
                    elif (P1_tmp < P1_lim and toglow == 1):
                        notice = Mailer()
                        notice.sendmail(P1_tmp, "L", P1_lim)
                        toglow = 0
                    # Email stuff end
    #            print (P1_tmp)
                    Pmax = float(txtPmax.get())
    #            print (Pmax)
                    if(P1_tmp > Pmax):
                        if(V1 == 'closed'):
                            GPIO.output(V1Channel,GPIO.HIGH)
                            V1 = 'open'
                        else:
                            if(V1 == 'open'):
                                GPIO.output(V1Channel,GPIO.LOW)
                                V1 = 'closed'
                        txtV1.delete(0,tkinter.END)
                        txtV1.insert(tkinter.END,V1)
                # LN2 valve
                    Pmin = float(txtPmin.get())
    #            print (Pmin)
                    if(P1_tmp < Pmin):
                        if(V2 == 'closed'):
                            GPIO.output(V2Channel,GPIO.HIGH)
                            V2 = 'open'
                    else:
                        if(V2 == 'open'):
                            GPIO.output(V2Channel,GPIO.LOW)
                            V2 = 'closed'
                    txtV2.delete(0,tkinter.END)
                    txtV2.insert(tkinter.END,V2)
                elif len(GaugeP1) != 17:
                    P1_tmp = None
            elif topstat == 0:
                print("Top pressure gauge port not found/open")
                P1_tmp = None

            if botstat == 1:
                # Presusre gauge 2
                #Gauge2.write(('$@253AD!002;FF').encode('utf8'))
                time.sleep(2*T_sleep)
                Gauge2.write(('$@253PR3?;FF').encode('utf8'))

                time.sleep(T_sleep)
                GaugeP2 = Gauge2.read(Gauge2.inWaiting()).decode('utf8')
                print('Jacket:' + GaugeP2 + " ;len = " +str(len(GaugeP2)))
                flag4 = 0
                while (len(GaugeP2) != 17 and flag4 <= 3):
                    print ('Pressure gauge (P2) readout error')
                    Gauge2.write(b'$@253PR3?;FF')
                    time.sleep(T_sleep)
                    try:
                        GaugeP2 = Gauge2.read(Gauge2.inWaiting()).decode('utf8')
                    except UnicodeDecodeError or UnicodeError:
                        pass
                    flag4 += 1
                #@253ACK1.37E-1;FF
                print (GaugeP2)
    #            print (len(GaugeP2))
                if len(GaugeP2) == 17:
                    bot_time = datetime.now()
                    bot_delta = bot_time - master_start
                    entPG2.delete(0, tkinter.END)
                    entPG2.insert(tkinter.END, format_time(bot_delta))
                    P2_tmp = float(GaugeP2[7:14])
                    txtP2.delete(0,tkinter.END)
                    txtP2.insert(tkinter.END,P2_tmp)
                elif len(GaugeP2) != 17:
                    P2_tmp = None
    #            print (P2_tmp)
            elif botstat == 0:
                print("Bottom pressure gauge port not found/open")
                P2_tmp = None
            
            values_pressure = [P1_tmp, P2_tmp]
            # insert
            cursor.setup(name_pressure, types = types_pressure)
            cursor.register(values_pressure)
                ###################### Thermometry ###############################
            
            cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = 'LAr_TPCruns_data', table_name = 'rtd')
            # table for pressure in db
            name_rtd = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5']
            types_rtd = ['FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT', 'FLOAT']
            
            if LLstat == 0:
                print("Arduino port not found/open")
                L0_tmp = None
                L1_tmp = None
                L2_tmp = None
                L3_tmp = None
                L4_tmp = None
                L5_tmp = None
            elif LLstat == 1:
                # Liquid Level Sensor
    #            LiquidLevel.write(b'R')
    #            time.sleep(T_sleep)
    #            LiquidLevelOut = LiquidLevel.read(LiquidLevel.inWaiting()).decode('utf8')
                LiquidLevelOut = LiquidLevel.readline().decode('utf8')
                flag5 = 0
                while (len(LiquidLevelOut) != 49 and flag5 <= 3):
                    print (LiquidLevelOut)
                    print ('Liquid Level Sensor readout error')
                    LiquidLevelOut = LiquidLevel.readline().decode('utf8')
                    flag5 += 1
               # print(LiquidLevelOut[0:46])
                if len(LiquidLevelOut) == 49:
                    print (LiquidLevelOut)
                    #A0_0540_A1_0540_A2_0540_A3_0540_A4_0540_A5_0540\n
                    #L0
                    ard_time = datetime.now()
                    ard_delta = ard_time - master_start
                    entLL.delete(0, tkinter.END)
                    entLL.insert(tkinter.END, format_time(ard_delta))

                    # Reading the ADC values
                    L_ADC = float(LiquidLevelOut[3:7])
                    L_V = float(L_ADC)*(5.0/1023.0)
                    L_R = L_V*1000./(5.0-L_V)
                    L0_tmp = -(math.sqrt(17.59246-0.00232*L_R)-3.908)/0.00116
                    L0_tmp = int(L0_tmp)
                    L0_tmpK = L0_tmp + 273.15
                    L0_correction = L0_tmpK - 8.05 # This is added because the displayed temp was 304.15 K when the room thermometer measured 296.10 K.
                    #L1
                    L_ADC = float(LiquidLevelOut[11:15])
                    L_V = float(L_ADC)*(5.0/1023.0)
                    L_R = L_V*1000./(5.0-L_V)
                    L1_tmp = -(math.sqrt(17.59246-0.00232*L_R)-3.908)/0.00116
                    L1_tmp = int(L1_tmp)
                    L1_tmpK = L1_tmp + 273.15
                    L1_correction = L1_tmpK + 0 # No correction for now
                    #L2
                    L_ADC = float(LiquidLevelOut[19:23])
                    L_V = float(L_ADC)*(5.0/1023.0)
                    L_R = L_V*1000./(5.0-L_V)
                    L2_tmp = -(math.sqrt(17.59246-0.00232*L_R)-3.908)/0.00116
                    L2_tmp = int(L2_tmp)
                    L2_tmpK = L2_tmp + 273.15
                    L2_correction = L2_tmpK + 0 # No correction for now
                    #L3
                    L_ADC = float(LiquidLevelOut[27:31])
                    L_V = float(L_ADC)*(5.0/1023.0)
                    L_R = L_V*1000./(5.0-L_V)
                    L3_tmp = -(math.sqrt(17.59246-0.00232*L_R)-3.908)/0.00116
                    L3_tmp = int(L3_tmp)
                    L3_tmpK = L3_tmp + 273.15
                    L3_correction = L3_tmpK + 0 # No correction for now
                    #L4
                    L_ADC = float(LiquidLevelOut[35:39])
                    L_V = float(L_ADC)*(5.0/1023.0)
                    L_R = L_V*1000./(5.0-L_V)
                    L4_tmp = -(math.sqrt(17.59246-0.00232*L_R)-3.908)/0.00116
                    L4_tmp = int(L4_tmp)
                    L4_tmpK = L4_tmp + 273.15
                    L4_correction = L4_tmpK - 28.05 # This is added because the displayed temp was 324.15 K when the room thermometer measured 296.10 K.
                    #L5
                    L_ADC = float(LiquidLevelOut[43:47])
                    L_V = float(L_ADC)*(5.0/1023.0)
                    L_R = L_V*1000./(5.0-L_V)
                    L5_tmp = -(math.sqrt(17.59246-0.00232*L_R)-3.908)/0.00116
                    L5_tmp = int(L5_tmp)
                    L5_tmpK = L5_tmp + 273.15
                    L5_correction = L5_tmpK - 24.05 # This is added because the displayed temp was 320.15 K when the room temperature measured 296.10 K.

                elif len(LiquidLevelOut) != 43:
                    L0_tmpK = None
                    L1_tmpK = None
                    L2_tmpK = None
                    L3_tmpK = None
                    L4_tmpK = None
                    L5_tmpK = None

                txtL0.delete(0, tkinter.END)
                txtL0.insert(tkinter.END, L0_correction)
                txtL1.delete(0,tkinter.END)
                txtL1.insert(tkinter.END,L1_correction)
                txtL2.delete(0,tkinter.END)
                txtL2.insert(tkinter.END,L2_correction)
                txtL3.delete(0,tkinter.END)
                txtL3.insert(tkinter.END,L3_correction)
                txtL4.delete(0,tkinter.END)
                txtL4.insert(tkinter.END,L4_correction)
                txtL5.delete(0,tkinter.END)
                txtL5.insert(tkinter.END,L5_correction)

#               print('Time : %.2f, Temperature : %.2f'%(time.perf_counter() - start_time,tempC))
#               if len(X) > 10:
#               del X[0]
#               X_max = X[0] + 14
#               del Y[0]
#           else:
#               X_max = 14
#           plt.cla()

                ax1.cla()
                ax2.cla()

                T1.append(T1_tmp)
                T2.append(T2_tmp)
                T3.append(T3_tmp)
                P1.append(P1_tmp)
                P2.append(P2_tmp)
                L0.append(L0_correction)
                L1.append(L1_correction)
                L2.append(L2_correction)
                L3.append(L3_correction)
                L4.append(L4_correction)
                L5.append(L5_correction)
                X.append(time.perf_counter() - start_time)
                LT.append(time.time())
                
                values_rtd = [float(L0_correction), float(L1_correction), float(L2_correction), float(L3_correction), float(L4_correction), float(L5_correction)]

                if(L0 != None and L1 != None and L2 != None and L3 != None and L4 != None and L5 != None):
                    # insert
                    cursor.setup(name_rtd, types = types_rtd)
                    cursor.register(values_rtd)

               # Creating the pandas dataframe that will save the data and using to_csv to save it.
                dict_to_save = {"Time":X,"EpochTime":LT,"Temp1":T1, "Temp2":T2, "Temp3":T3, "TopPress":P1, "BotPress":P2, "L0Temp":L0, "L1Temp":L1, "L2Temp":L2, "L3Temp":L3, "L4Temp":L4, "L5Temp":L5}
                df_to_save = pd.DataFrame(dict_to_save)
                save_file = df_to_save.to_csv(sep=",",path_or_buf=format_str,mode=filestat)
                print("Saved file")
               # ax1.plot(X,T1,label="T1")
               # ax1.plot(X,T2,label="T2")
               # ax1.plot(X,T3,label="T3")
                ax1.plot(X, L0, label="L0")
                ax1.plot(X,L1,label="L1")
                ax1.plot(X,L2,label="L2")
                ax1.plot(X,L3,label="L3")
                ax1.plot(X,L4,label="L4")
                ax1.plot(X,L5,label="L5")
                ax1.legend(loc="lower left")

                ax2.plot(X,P1,label="P1")
                ax2.plot(X,P2,label="P2")
                ax2.set_yscale('log')
                ax2.legend()

#           plt.ylim(0, 50)
#           plt.xlim(X[0], X_max)
#           plt.xlabel('Time [s]')
#           plt.ylabel('Temperature [deg]')
                canvas.draw()
                window.update()
#           plt.pause(1)
                # add saving comment here

def stop():
    global flg,Compressor,Gauge1,Gauge2
    res = messagebox.askyesno("End the program", "Are you sure to end the program?")
#    print (res)
    if res == True:
        GPIO.cleanup()
        flg = False
        Compressor.close()
        Gauge1.close()
        Gauge2.close()
        LiquidLevel.close()
        window.destroy()

def CompressorOn():
    global Compressor
    res = messagebox.askyesno("Compressor on", "Are you sure to turn on the Compressor?")
#    print (res)
    if res == True:
        print ('turning on the compressor')
        Compressor.write(b'$ON177CF\r')
        time.sleep(1)

def CompressorOff():
    global Compressor
    res = messagebox.askyesno("Compressor off", "Are you sure to turn off the Compressor?")
#    print (res)
    if res == True:
        print ('turning off the compressor')
        Compressor.write(b'$OFF9188\r')
        time.sleep(1)

# Adding functionality to turn heater relay on using a button
def HeaterOn():
    global HeaterCtrl
    res = messagebox.askyesno("Heater On", "Are you sure you want to turn the heater on?")
    if res == True:
        print ("Turning the heater on")
        GPIO.output(HeaterCtrl, GPIO.HIGH)
        time.sleep(1)

def HeaterOff():
    global HeaterCtrl
    res = messagebox.askyesno("Heater Off", "Are you sure you want to turn the heater off?")
    if res == True:
        print ("Turning the heater off")
        GPIO.output(HeaterCtrl, GPIO.LOW)
        time.sleep(1)

def popupwin():
    popup = tk.Toplevel()
    popup.title("Settings")
    popup.geometry("400x330")

    def changestat():
        val = var.get()
        if val == "CE":
            compstat = 1
        elif val == "CD":
            compstat = 0
        elif val == "TE":
            topstat = 1
        elif val == "TD":
            topstat = 0
        elif val == "BE":
            botstat = 1
        elif val == "BD":
            botstat = 0
        elif val == "LLE":
            LLstat = 1
        elif val == "LLD":
            LLstat = 0
        else:
            raise Exception("Invalid value provided to function.")

    def setsavemode():
       # pass
        val = filemode.get()
        if val == "a":
            filestat = val
            format_str = filedialog.askopenfilename()
        elif val == "w":
            filestat = val
        else:
            raise Exception("Invalid value provided to function")

    # Labels
    sett1lbl = tk.Label(popup, text="Enable/Disable Devices", pady=10, padx=5).grid(row=0, column=0)
    comp1lbl = tk.Label(popup, text="Compressor").grid(row=1, column=0)
    top1lbl = tk.Label(popup, text="Top pressure gauge").grid(row=2, column=0)
    bot1lbl = tk.Label(popup, text="Bottom pressure gauge").grid(row=3, column=0)
    LL1lbl = tk.Label(popup, text="LL/Arduino").grid(row=4, column=0)
    sett2lbl = tk.Label(popup, text="ON/OFF Settings", padx=5, pady=10).grid(row=5, column=0)
    comp2lbl = tk.Label(popup, text="Compressor").grid(row=6, column=0)
    heatpwrlbl = tk.Label(popup, text="Heater Power").grid(row=7, column=0)
    save1lbl = tk.Label(popup, text="File Save Options", padx=5, pady=10).grid(row=8, column=0)
    save2lbl = tk.Label(popup, text="Mode to save file:").grid(row=9, column=0)

    # Buttons
    componbtn = tk.Button(popup, text="ON", command=CompressorOn)
    componbtn.grid(row=6, column=1)
    compoffbtn = tk.Button(popup, text="OFF", command=CompressorOff)
    compoffbtn.grid(row=6, column=2)
    heatonbtn = tk.Button(popup, text="ON", command=HeaterOn)
    heatonbtn.grid(row=7, column=1)
    heatoffbtn = tk.Button(popup, text="OFF", command=HeaterOff)
    heatoffbtn.grid(row=7, column=2)
    exitbtn = tk.Button(popup, text="Exit", command=popup.destroy)
    exitbtn.grid(row=10, column=2)

    # Radiobuttons
    var = tk.StringVar()
    filemode = tk.StringVar()
    compen = tk.Radiobutton(popup, text="Enable", variable=var, value="CE", command=changestat).grid(row=1,column=1)
    compdis = tk.Radiobutton(popup, text="Disable", variable=var, value="CD", command=changestat).grid(row=1,column=2)
    topen = tk.Radiobutton(popup, text="Enable", variable=var, value="TE", command=changestat).grid(row=2,column=1)
    topdis = tk.Radiobutton(popup, text="Disable", variable=var, value="TD", command=changestat).grid(row=2,column=2)
    boten = tk.Radiobutton(popup, text="Enable", variable=var, value="BE", command=changestat).grid(row=3,column=1)
    botdis = tk.Radiobutton(popup, text="Disable", variable=var, value="BD", command=changestat).grid(row=3,column=2)
    LLen = tk.Radiobutton(popup, text="Enable", variable=var, value="LLE", command=changestat).grid(row=4,column=1)
    LLdis = tk.Radiobutton(popup, text="Disable", variable=var, value="LLD", command=changestat).grid(row=4,column=2)
    fileapp = tk.Radiobutton(popup, text="Append", variable=filemode, value="a", command=setsavemode).grid(row=8,column=1)
    filenew = tk.Radiobutton(popup, text="Write new file", variable=filemode, value="w", command=setsavemode).grid(row=8,column=2)

if __name__ == '__main__':
    flg = True
    try:
        window = tk.Tk()
        window.geometry('1010x600')
        window.title('GRAMS Housekeeping')
#        window.withdraw()
#        window.protocol('WM_DELETE_WINDOW', destroy)  # When you close the tkinter window.
        #row 1
        lblPG1=tk.Label(window,text='Pressure Gauge 1 (top)')
        lblPG1.grid(row=1,column=0,columnspan=1)
        entPG1 = tk.Entry(width=10, justify="right")
        #entPG1.insert(0, toppath)
       #cbPG1 = ttk.Combobox(window, values=devices, style="office.TCombobox", width=12)
       #cbPG1.set('/dev/ttyUSB0')
        entPG1.grid(row=1,column=1,columnspan=1)

        lblPG2=tk.Label(window,text='Pressure Gauge 2 (bot)')
        lblPG2.grid(row=1,column=2,columnspan=1)
        entPG2 = tk.Entry(width=10, justify="right")
        #entPG2.insert(0, botpath)
       #cbPG2 = ttk.Combobox(window, values=devices, style="office.TCombobox",width=12)
       #cbPG2.set('/dev/ttyUSB1')
        entPG2.grid(row=1,column=3,columnspan=1)

        lblP1=tk.Label(window,text='P1 [torr]')
        lblP1.grid(row=1,column=4)
        txtP1=tkinter.Entry(width=7,justify='right')
        txtP1.grid(row=1,column=5)

        lblP2=tk.Label(window,text='P2 [torr]')
        lblP2.grid(row=1,column=6)
        txtP2=tkinter.Entry(width=7,justify='right')
        txtP2.grid(row=1,column=7)

        btnStart = tkinter.Button(window, text='Start', command=loop)
        btnStart.grid(row=1,column=9,padx=5)

        btnStop = tkinter.Button(window, text='Stop', command=stop)
        btnStop.grid(row=1,column=10,padx=5)

        #row 2
        lblLL=tk.Label(window,text='Liquid Level Sensor')
        lblLL.grid(row=2,column=0)
        entLL = tk.Entry(width=10, justify="right")
        #entLL.insert(0, ardpath)
        #cbLL = ttk.Combobox(window, values=devices, style="office.TCombobox", width=12)
        #cbLL.set('/dev/ttyACM0')
        entLL.grid(row=2,column=1)

        lblCompressor=tk.Label(window,text='Compressor')
        lblCompressor.grid(row=2,column=2)
        entCompressor = tk.Entry(width=10, justify="right")
        #entCompressor.insert(0, compresspath)
        #cbCompressor = ttk.Combobox(window, values=devices, style="office.TCombobox", width=12)
        #cbCompressor.set('/dev/ttyUSB2')
        entCompressor.grid(row=2,column=3)

        settbtn = tk.Button(window, text="Settings", command=popupwin)
        settbtn.grid(row=2, column=9)
#        btnCompressorOn = tkinter.Button(window, text='On', command=CompressorOn)
#        btnCompressorOn.grid(row=2,column=9,padx=5)

#        btnCompressorOff = tkinter.Button(window, text='Off', command=CompressorOff)
#        btnCompressorOff.grid(row=2,column=10,padx=5)

        #row 3
        lblT1=tk.Label(window,text='T1 [deg]')
        lblT1.grid(row=3,column=4)
        txtT1=tkinter.Entry(width=7,justify='right')
        txtT1.grid(row=3,column=5)

        lblT2=tk.Label(window,text='T2 [deg]')
        lblT2.grid(row=3,column=6)
        txtT2=tkinter.Entry(width=7,justify='right')
        txtT2.grid(row=3,column=7)

        lblT3=tk.Label(window,text='T3 [deg]')
        lblT3.grid(row=3,column=8)
        txtT3=tkinter.Entry(width=7,justify='right')
        txtT3.grid(row=3,column=9)

        #row 4

        lblL0 = tk.Label(window, text="L0 [K]")
        lblL0.grid(row=4, column=0)
        txtL0 = tkinter.Entry(width=7, justify="right")
        txtL0.grid(row=4, column=1)
        lblL1=tk.Label(window,text='L1 [K]')
        lblL1.grid(row=4,column=2)
        txtL1=tkinter.Entry(width=7,justify='right')
        txtL1.grid(row=4,column=3)

        lblL2=tk.Label(window,text='L2 [K]')
        lblL2.grid(row=4,column=4)
        txtL2=tkinter.Entry(width=7,justify='right')
        txtL2.grid(row=4,column=5)

        lblL3=tk.Label(window,text='L3 [K]')
        lblL3.grid(row=4,column=6)
        txtL3=tkinter.Entry(width=7,justify='right')
        txtL3.grid(row=4,column=7)

        lblL4=tk.Label(window,text='L4 [K]')
        lblL4.grid(row=4,column=8)
        txtL4=tkinter.Entry(width=7,justify='right')
        txtL4.grid(row=4,column=9)

        lblL5=tk.Label(window,text='L5 [K]')
        lblL5.grid(row=4,column=10)
        txtL5=tkinter.Entry(width=7,justify='right')
        txtL5.grid(row=4,column=11)

        #row 5
        lblPmax=tk.Label(window,text=u'Pmax [torr]')
        lblPmax.grid(row=5,column=0)
        txtPmax=tkinter.Entry(width=7,justify='right')
        txtPmax.grid(row=5,column=1)
        txtPmax.insert(tkinter.END,'1500')

        lblPmin=tk.Label(window,text=u'Pmin [torr]')
        lblPmin.grid(row=5,column=2)
        txtPmin=tkinter.Entry(width=7,justify='right')
        txtPmin.grid(row=5,column=3)
        txtPmin.insert(tkinter.END,'1')

        lblV1=tk.Label(window,text='Vout (Pin-2)')
        lblV1.grid(row=5,column=4)
        txtV1=tkinter.Entry(width=7,justify='center')
        txtV1.grid(row=5,column=5)

        lblV2=tk.Label(window,text='Vin (Pin-x)')
        lblV2.grid(row=5,column=6)
        txtV2=tkinter.Entry(width=7,justify='center')
        txtV2.grid(row=5,column=7)

        lblStatus=tk.Label(window,text='Status')
        lblStatus.grid(row=5,column=8)
        txtStatus=tkinter.Entry(width=7,justify='center')
        txtStatus.grid(row=5,column=9)


        #row 6: figures
        canvas = FigureCanvasTkAgg(fig,window)
        canvas.get_tk_widget().grid(row=6,column=0,columnspan=10,pady=5)
#        canvas.get_tk_widget().pack()
#        toolbar=NavigationToolbar2Tk(canvas,window)

        #row 7: navigation toolbar
        toolbarFrame = tk.Frame(master=window)
        toolbarFrame.grid(row=7,column=0,columnspan=10)
        toolbar = NavigationToolbar2Tk(canvas,toolbarFrame)

        window.mainloop()
    
    except KeyboardInterrupt:
        stop()

#def destroy():
#    Compressor.close()

#if __name__ == '__main__':
#    print ('Program is starting ... ')
#    #setup()
#    try:
#        loop()
#    except KeyboardInterrupt:
#        destroy()
