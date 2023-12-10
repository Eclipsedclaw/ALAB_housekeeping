# ALAB_housekeeping
housekeeping script for aramaki lab

# How to start the UI
1. To simply run this code, go to Terminal (on your own machine or on the Raspberry Pi) and execute this command.
```
python ~/code/Housekeeping.py
```
   If you want to use the GUI, then you have to use VNC Viewer to be able to see the user interface window.

2. At first, the code will not run anything visible on the GUI. You need to press the "START" button for the code to start the serial communication with the various sensors/gauges.
  
<img width="1025" alt="Screen Shot 2023-08-09 at 2 25 18 PM" src="https://github.com/Eclipsedclaw/ALAB_housekeeping/assets/59633001/efc87a70-adcd-4ccc-bf9b-917cb20f62b6">

3. Once the "START" button is pressed, the program will start receiving responses from the various connected devices. You will be able to see the decoded responses in the Terminal window. These values should automatically start updating on the GUI as well.

4. Please do not press the "ON" and "OFF" buttons for now. These are intended to start and stop the compressor. Unless you want to start/stop the compressor, it's advised to not use these buttons.
