# ALAB_housekeeping
housekeeping script for aramaki lab using pyqt5

# How to start the UI
1. To simply run this code, go to Terminal (on your own machine or on the Raspberry Pi) and execute this command.
```
python ./HK.py
```
   If you want to use the GUI, then you have to use VNC Viewer to be able to see the user interface window.

2. At first, the code will not run anything visible on the GUI. You need to press the "START HOUSEKEEPING SYSTEM" button for the code to start the serial communication with the various sensors/gauges.

3. Once the "START" button is pressed, the program will start receiving responses from the various connected devices. You will be able to see the decoded responses in the Terminal window. These values should automatically start updating on the GUI as well.
![image](https://github.com/Eclipsedclaw/ALAB_housekeeping/assets/37788723/815f612c-d92f-4d13-b5b4-86addbbd6914)

4. For control buttons such as heater and compressor control, it is suggested to use after asking people who understand their functionality. Do not click them without understanding what they do.


# How to run the turbo codes
1. To turn on the turbo, run:
```
python turbo_ON.py
```
to turn off, run:
```
python turbo_OFF.py
```

2. To read the turbo condition, e.g., its rotation speed, drive current, error codes, etc., run:
```
python check_turbo_readout.py
```
It's better to run this code in a tmux or screen session (or use nohup), so that it can keep recording the turbo condition even when you close the programming window.
After running the readout code, you will first be asked to input the USB port for the turbo.
<img width="517" height="61" alt="image" src="https://github.com/user-attachments/assets/0b62117a-049f-4f57-9459-847d6129e4b7" />

The port for the turbo is usually USBx, where x is not 0. Here, for example, is 1. So input 1, then the code will be running.
<img width="516" height="195" alt="image" src="https://github.com/user-attachments/assets/0a755bef-ac98-47d0-a832-864afe7bf4f8" />

You can monitor the turbo condition from the output in terminal, or go to the Turbo Page on Grafana:
http://aramakilab.neu.edu:3000/d/beonjxv3kaj9ce/turbo-page?orgId=1&from=now-1h&to=now&timezone=browser&refresh=auto

3. To quickly test if the remote control is working, you can run
```
python check_turbo_rpm.py
```
to read the rotation speed only.
