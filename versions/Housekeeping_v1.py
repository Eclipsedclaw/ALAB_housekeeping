import time
import math

import serial
from serial.tools import list_ports

import tkinter as tk
import tkinter.scrolledtext
from tkinter import ttk

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

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
ax2 = fig.add_subplot(1, 2, 2)
plt.subplots_adjust(wspace=0.3)
T1,T2,T3,P1,X = [],[],[],[],[]
start_time = time.perf_counter()

Compressor = None
Gauge = None

def loop():
    global Compressor
    global Gauge
    global flg
    #Compressor: /dev/ttyUSB1
    Compressor = serial.Serial(cbCompressor.get())
#    Compressor.port = cbCompressor.get()
    Compressor.baudrate = 9600
    Compressor.parity = 'N'
    Compressor.stopbits = 1
    Compressor.bytesize = 8

    #Pressure Gauge: /dev/ttyUSB2
    Gauge = serial.Serial(cbPG.get())
#    Gauge.port = cbPG.get()
    Gauge.baudrate = 9600
    Gauge.parity = 'N'
    Gauge.stopbits = 1
    Gauge.bytesize = 8
    print('start the program')
    while True:
        if flg == False:
            print('stop the program')
            flg = True
            break
        else:
            Compressor.write(b'$TEAA4B9\r')
            time.sleep(0.6)
            Gauge.write(b'$@253PR3?;FF')
#            Gauge.write(b'$@253PR4?;FF')
            time.sleep(0.6)
            #while Compressor.inWaiting() > 0:
            CompressorOut = Compressor.read(Compressor.inWaiting()).decode('utf8')
            T1_tmp = CompressorOut[6:8]
            T2_tmp = CompressorOut[10:12]
            T3_tmp = CompressorOut[14:16]
            print (T1_tmp,T2_tmp,T3_tmp)
            GaugeOut = Gauge.read(Gauge.inWaiting()).decode('utf8')
            P1_tmp = GaugeOut[7:14]
#            P1_tmp = GaugeOut[7:15]
            txtP1.delete(0.,tk.END)
            txtT1.delete(0.,tk.END)
            txtT2.delete(0.,tk.END)
            txtT3.delete(0.,tk.END)
            txtP1.insert('1.0',P1_tmp,"right")
            txtT1.insert('1.0',T1_tmp,"right")
            txtT2.insert('1.0',T2_tmp,"right")
            txtT3.insert('1.0',T3_tmp,"right")
            print (P1_tmp)
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
            P1.append(float(P1_tmp))
            T1.append(int(T1_tmp))
            T2.append(int(T2_tmp))
            T3.append(int(T3_tmp))
            X.append(time.perf_counter() - start_time)

            ax1.set_title("Temperature [deg]")
            ax1.set_xlabel("Time [s]")
            ax1.set_ylabel("Temperature [deg]")
            ax1.plot(X,T1,label="T1")
            ax1.plot(X,T2,label="T2")
            ax1.plot(X,T3,label="T3")
            ax1.legend()

            ax2.plot(X,P1,label="P1")
            ax2.set_title("Pressure [Torr]")
            ax2.set_xlabel("Time [s]")
            ax2.set_ylabel("Pressure [Torr]")
            ax2.legend()

#           plt.ylim(0, 50)
#           plt.xlim(X[0], X_max)
#           plt.xlabel('Time [s]')
#           plt.ylabel('Temperature [deg]')
            canvas.draw()
            window.update()
#           plt.pause(1)

def stop():
    global flg
    global Compressor
    global Gauge
    flg = False
    Compressor.close()
    Gauge.close()
    window.destroy()

if __name__ == '__main__':
    flg = True
    try:
        window = tk.Tk()
        window.geometry('900x500')
        window.title('GRAMS Housekeeping')
#        window.withdraw()
#        window.protocol('WM_DELETE_WINDOW', destroy)  # When you close the tkinter window.       

        lblCompressor=tk.Label(window,text='Compressor')
        lblCompressor.grid(row=1,column=0,columnspan=2)
        cbCompressor = ttk.Combobox(window, values=devices, style="office.TCombobox")
        cbCompressor.set('/dev/ttyUSB1')
        cbCompressor.grid(row=1,column=2,columnspan=2)

        lblPG=tk.Label(window,text='Pressure Gauge')
        lblPG.grid(row=1,column=4,columnspan=2)
        cbPG = ttk.Combobox(window, values=devices, style="office.TCombobox")
        cbPG.set('/dev/ttyUSB2')
        cbPG.grid(row=1,column=6,columnspan=2)

        btnStart = tkinter.Button(window, text='Start', command=loop)
        btnStart.grid(row=1,column=8,padx=5)

        btnStop = tkinter.Button(window, text='Stop', command=stop)
        btnStop.grid(row=2,column=8,padx=5)

        lblP1=tk.Label(window,text='P1 [torr]')
        lblP1.grid(row=2,column=0)
        txtP1=tkinter.Text(height=1,width=8)
        txtP1.grid(row=2,column=1)
        txtP1.tag_configure("right", justify='right')

        lblT1=tk.Label(window,text='T1 [deg]')
        lblT1.grid(row=2,column=2)
        txtT1=tkinter.Text(height=1,width=3)
        txtT1.grid(row=2,column=3)
        txtT1.tag_configure("right", justify='right')

        lblT2=tk.Label(window,text='T2 [deg]')
        lblT2.grid(row=2,column=4)
        txtT2=tkinter.Text(height=1,width=3)
        txtT2.grid(row=2,column=5)
        txtT2.tag_configure("right", justify='right')

        lblT3=tk.Label(window,text='T3 [deg]')
        lblT3.grid(row=2,column=6)
        txtT3=tkinter.Text(height=1,width=3)
        txtT3.grid(row=2,column=7)
        txtT3.tag_configure("right", justify='right')

        canvas = FigureCanvasTkAgg(fig,window)
        canvas.get_tk_widget().grid(row=3,column=0,columnspan=9,pady=5)
#        canvas.get_tk_widget().pack()
#        toolbar=NavigationToolbar2Tk(canvas,window)
        # navigation toolbar
        toolbarFrame = tk.Frame(master=window)
        toolbarFrame.grid(row=4,column=0,columnspan=9)
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
