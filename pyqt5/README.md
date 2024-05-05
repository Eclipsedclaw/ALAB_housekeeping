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
