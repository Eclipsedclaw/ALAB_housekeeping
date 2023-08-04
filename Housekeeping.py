import time
import math

import serial
from serial.tools import list_ports

import tkinter as tk
import tkinter.scrolledtext
from tkinter import ttk
from tkinter import messagebox

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import RPi.GPIO as GPIO

# GPIO setting
GPIO.setmode(GPIO.BCM)
V1 = 'closed'
V2 = 'closed'
V1Channel = 2
V2Channel = 2
GPIO.setup(V1Channel,GPIO.OUT)
GPIO.setup(V2Channel,GPIO.OUT)

# search serial port
ser = serial.Serial()
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)

#fig = plt.figure()
fig = plt.figure(figsize=(9,4))
#plt.rcParams["font.size"] = 14
#plt.grid()
ax1 = fig.add_subplot(1, 2, 1)
ax1.set_title("Temperature [deg]")
ax1.set_xlabel("Time [s]")
ax1.set_ylabel("Temperature [deg]")
ax2 = fig.add_subplot(1, 2, 2)
ax2.set_title("Pressure [Torr]")
ax2.set_xlabel("Time [s]")
ax2.set_ylabel("Pressure [Torr]")

plt.subplots_adjust(wspace=0.3)
T1,T2,T3,P1,P2,X = [],[],[],[],[],[]
L0,L1,L2,L3,L4,L5 = [],[],[],[],[],[]
start_time = time.perf_counter()

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

Gauge2 = serial.Serial()
botpath = "/dev/botpress"
Gauge2.baudrate = 9600
Gauge2.parity = 'N'
Gauge2.stopbits = 1
Gauge2.bytesize = 8

LiquidLevel = serial.Serial()
ardpath = "/dev/arduino"
LiquidLevel.baudrate = 9600
LiquidLevel.parity = 'N'
LiquidLevel.stopbits = 1
LiquidLevel.bytesize = 8

Error = 0
T_sleep = 0.6 #sleep time

def loop():
    global Compressor,Gauge1,Gauge2,flg,Error,V1,V2
 
    #Compressor: /dev/ttyUSB2
#    print (cbCompressor.get())
    Compressor = serial.Serial(compresspath)
#    Compressor.port = cbCompressor.get()
#    Compressor.baudrate = 9600
#    Compressor.parity = 'N'
#    Compressor.stopbits = 1
#    Compressor.bytesize = 8
#    Compressor.timeout = T_sleep

    #Pressure Gauge1: /dev/ttyUSB0
#    print (cbPG1.get())
    Gauge1 = serial.Serial(toppath)
#    Gauge1.port = cbPG1.get()
#    Gauge1.baudrate = 9600
#    Gauge1.parity = 'N'
#    Gauge1.stopbits = 1
#    Gauge1.bytesize = 8
#    Gauge1.timeout = T_sleep

    #Pressure Gauge2: /dev/ttyUSB1
#    print (cbPG2.get())
    # This is the bottom pressure gauge
    Gauge2 = serial.Serial(botpath)
#    Gauge2.port = cbPG2.get() 
#    Gauge2.baudrate = 9600
#    Gauge2.parity = 'N'
#    Gauge2.stopbits = 1
#    Gauge2.bytesize = 8
#    Gauge2.timeout = T_sleep

    #Liquid Level Sensor: /dev/ttyACM0 # Now permanently at /dev/arduino. - Robin
    LiquidLevel = serial.Serial(ardpath)

    print('start the program')
    while True:
        if flg == False:
            print('stop the program')
            flg = True
            break
        else:
            # Compressor temperature
            Compressor.write(b'$TEAA4B9\r')
            time.sleep(T_sleep)
            CompressorOut = Compressor.read(Compressor.inWaiting()).decode('utf8')
            while not (len(CompressorOut) == 26):
                print ('Compressor temperature readout error')
                Compressor.write(b'$TEAA4B9\r')
                time.sleep(T_sleep)
                CompressorOut = Compressor.read(Compressor.inWaiting()).decode('utf8')
            #$TEA,021,015,015,000,6F37
            print (CompressorOut)
#            print (len(CompressorOut))
            T1_tmp = float(CompressorOut[6:8])
            txtT1.delete(0,tkinter.END)
            txtT1.insert(tkinter.END,T1_tmp)
            T2_tmp = float(CompressorOut[10:12])
            txtT2.delete(0,tkinter.END)
            txtT2.insert(tkinter.END,T2_tmp)
            T3_tmp = float(CompressorOut[14:16])
            txtT3.delete(0,tkinter.END)
            txtT3.insert(tkinter.END,T3_tmp)
#            print (T1_tmp,T2_tmp,T3_tmp)

            # Compressor status
            Compressor.write(b'$STA3504\r')
            time.sleep(T_sleep)
            CompressorOut = Compressor.read(Compressor.inWaiting()).decode('utf8')
            while not (len(CompressorOut) == 15):
                print ('Compressor status readout error')
                Compressor.write(b'$STA3504\r')
                time.sleep(T_sleep)
                CompressorOut = Compressor.read(Compressor.inWaiting()).decode('utf8')
            #$STA,0000,FAD0
            print (CompressorOut)
#            print (len(CompressorOut))
            Status_tmp = CompressorOut[5:9]
            if(Status_tmp == '0000' and Error == 0): Status = 'OFF'
            elif(Status_tmp == '0301'and Error == 0): Status = 'OK'
            else: 
                Status = 'ERROR'
                Error = 1 
            txtStatus.delete(0,tkinter.END)
            txtStatus.insert(tkinter.END,Status)
#            print (Status_tmp)

            # Presusre gauge 1
            Gauge1.write(b'$@253PR3?;FF')
#            Gauge.write(b'$@253PR4?;FF')
            time.sleep(T_sleep)
            GaugeP1 = Gauge1.read(Gauge1.inWaiting()).decode('utf8')
            while not (len(GaugeP1) == 17):
                print ('Pressure gauge (P1) readout error')
                Gauge1.write(b'$@253PR3?;FF')
                time.sleep(T_sleep)
                GaugeP1 = Gauge1.read(Gauge1.inWaiting()).decode('utf8')
            #@253ACK6.41E+2;FF
            print (GaugeP1)
#            print (len(GaugeP1))
            P1_tmp = float(GaugeP1[7:14])
#            P1_tmp = GaugeOut[7:15]
            txtP1.delete(0,tkinter.END)
            txtP1.insert(tkinter.END,P1_tmp)
#            print (P1_tmp)

            # Presusre gauge 2
            Gauge2.write(b'$@253PR3?;FF')
            time.sleep(T_sleep)
            GaugeP2 = Gauge2.read(Gauge2.inWaiting()).decode('utf8')
            while not (len(GaugeP2) == 17):
                print ('Pressure gauge (P2) readout error')
                Gauge2.write(b'$@253PR3?;FF')
                time.sleep(T_sleep)
                GaugeP2 = Gauge2.read(Gauge2.inWaiting()).decode('utf8')
            #@253ACK1.37E-1;FF
            print (GaugeP2)
#            print (len(GaugeP2))
            P2_tmp = float(GaugeP2[7:14])
            txtP2.delete(0,tkinter.END)
            txtP2.insert(tkinter.END,P2_tmp)
#            print (P2_tmp)

            # Releae valve
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

            # Liquid Level Sensor 
#            LiquidLevel.write(b'R')
#            time.sleep(T_sleep)
#            LiquidLevelOut = LiquidLevel.read(LiquidLevel.inWaiting()).decode('utf8')
            LiquidLevelOut = LiquidLevel.readline().decode('utf8')
            while not (len(LiquidLevelOut) == 43):
                print ('Liquid Level Sensor readout error')
                LiquidLevelOut = LiquidLevel.readline().decode('utf8')
            print(LiquidLevelOut[0:42])
            #A0_540_A1_540_A2_540_A3_540_A4_540_A5_540\n
            #L0
            L_ADC = float(LiquidLevelOut[3:6])
            L_V = float(L_ADC)*(5.0/1023.0)
            L_R = L_V*1000./(5.0-L_V)
            L0_tmp = -(math.sqrt(17.59246-0.00232*L_R)-3.908)/0.00116
            L0_tmp = int(L0_tmp)
            #L1
            L_ADC = float(LiquidLevelOut[10:13])
            L_V = float(L_ADC)*(5.0/1023.0)
            L_R = L_V*1000./(5.0-L_V)
            L1_tmp = -(math.sqrt(17.59246-0.00232*L_R)-3.908)/0.00116
            L1_tmp = int(L1_tmp)
            #L2
            L_ADC = float(LiquidLevelOut[17:20])
            L_V = float(L_ADC)*(5.0/1023.0)
            L_R = L_V*1000./(5.0-L_V)
            L2_tmp = -(math.sqrt(17.59246-0.00232*L_R)-3.908)/0.00116
            L2_tmp = int(L2_tmp)
            #L3
            L_ADC = float(LiquidLevelOut[24:27])
            L_V = float(L_ADC)*(5.0/1023.0)
            L_R = L_V*1000./(5.0-L_V)
            L3_tmp = -(math.sqrt(17.59246-0.00232*L_R)-3.908)/0.00116
            L3_tmp = int(L3_tmp)
            #L4
            L_ADC = float(LiquidLevelOut[31:34])
            L_V = float(L_ADC)*(5.0/1023.0)
            L_R = L_V*1000./(5.0-L_V)
            L4_tmp = -(math.sqrt(17.59246-0.00232*L_R)-3.908)/0.00116
            L4_tmp = int(L4_tmp)
            #L5
            L_tmp = float(LiquidLevelOut[38:41])
            L_V = float(L_ADC)*(5.0/1023.0)
            L_R = L_V*1000./(5.0-L_V)
            L5_tmp = -(math.sqrt(17.59246-0.00232*L_R)-3.908)/0.00116
            L5_tmp = int(L5_tmp)

            txtL1.delete(0,tkinter.END)
            txtL1.insert(tkinter.END,L1_tmp)
            txtL2.delete(0,tkinter.END)
            txtL2.insert(tkinter.END,L2_tmp)
            txtL3.delete(0,tkinter.END)
            txtL3.insert(tkinter.END,L3_tmp)
            txtL4.delete(0,tkinter.END)
            txtL4.insert(tkinter.END,L4_tmp)
            txtL5.delete(0,tkinter.END)
            txtL5.insert(tkinter.END,L5_tmp)

#           print('Time : %.2f, Temperature : %.2f'%(time.perf_counter() - start_time,tempC))
#           if len(X) > 10:
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
            L0.append(L0_tmp)
            L1.append(L1_tmp)
            L2.append(L2_tmp)
            L3.append(L3_tmp)
            L4.append(L4_tmp)
            L5.append(L5_tmp)
            X.append(time.perf_counter() - start_time)

            ax1.plot(X,T1,label="T1")
            ax1.plot(X,T2,label="T2")
            ax1.plot(X,T3,label="T3")
            ax1.plot(X,L1,label="L1")
            ax1.plot(X,L2,label="L2")
            ax1.plot(X,L3,label="L3")
            ax1.plot(X,L4,label="L4")
            ax1.plot(X,L5,label="L5")
            ax1.legend()

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

if __name__ == '__main__':
    flg = True
    try:
        window = tk.Tk()
        window.geometry('900x600')
        window.title('GRAMS Housekeeping')
#        window.withdraw()
#        window.protocol('WM_DELETE_WINDOW', destroy)  # When you close the tkinter window.       

        #row 1
        lblPG1=tk.Label(window,text='Pressure Gauge 1 (top)')
        lblPG1.grid(row=1,column=0,columnspan=1)
        entPG1 = tk.Entry(width=7, justify="right")
        entPG1.insert(0, toppath)
       #cbPG1 = ttk.Combobox(window, values=devices, style="office.TCombobox", width=12)
       #cbPG1.set('/dev/ttyUSB0')
        entPG1.grid(row=1,column=1,columnspan=1)

        lblPG2=tk.Label(window,text='Pressure Gauge 2 (bot)')
        lblPG2.grid(row=1,column=2,columnspan=1)
        entPG2 = tk.Entry(width=7, justify="right")
        entPG2.insert(0, botpath)
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
        btnStart.grid(row=1,column=8,padx=5)

        btnStop = tkinter.Button(window, text='Stop', command=stop)
        btnStop.grid(row=1,column=9,padx=5)

        #row 2
        lblLL=tk.Label(window,text='Liquid Level Sensor')
        lblLL.grid(row=2,column=0)
        entLL = tk.Entry(width=7, justify="right")
        entLL.insert(0, ardpath)
        #cbLL = ttk.Combobox(window, values=devices, style="office.TCombobox", width=12)
        #cbLL.set('/dev/ttyACM0')
        entLL.grid(row=2,column=1)

        lblCompressor=tk.Label(window,text='Compressor')
        lblCompressor.grid(row=2,column=2)
        entCompressor = tk.Entry(width=7, justify="right")
        ent.insert(0, compresspath)
        #cbCompressor = ttk.Combobox(window, values=devices, style="office.TCombobox", width=12)
        #cbCompressor.set('/dev/ttyUSB2')
        entCompressor.grid(row=2,column=3)

        btnCompressorOn = tkinter.Button(window, text='On', command=CompressorOn)
        btnCompressorOn.grid(row=2,column=8,padx=5)

        btnCompressorOff = tkinter.Button(window, text='Off', command=CompressorOff)
        btnCompressorOff.grid(row=2,column=9,padx=5)

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
        lblL1=tk.Label(window,text='L1 [deg]')
        lblL1.grid(row=4,column=0)
        txtL1=tkinter.Entry(width=7,justify='right')
        txtL1.grid(row=4,column=1)

        lblL2=tk.Label(window,text='L2 [deg]')
        lblL2.grid(row=4,column=2)
        txtL2=tkinter.Entry(width=7,justify='right')
        txtL2.grid(row=4,column=3)

        lblL3=tk.Label(window,text='L3 [deg]')
        lblL3.grid(row=4,column=4)
        txtL3=tkinter.Entry(width=7,justify='right')
        txtL3.grid(row=4,column=5)

        lblL4=tk.Label(window,text='L4 [deg]')
        lblL4.grid(row=4,column=6)
        txtL4=tkinter.Entry(width=7,justify='right')
        txtL4.grid(row=4,column=7)

        lblL5=tk.Label(window,text='L5 [deg]')
        lblL5.grid(row=4,column=8)
        txtL5=tkinter.Entry(width=7,justify='right')
        txtL5.grid(row=4,column=9)
        
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
