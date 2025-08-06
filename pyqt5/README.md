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
1. First of all, quickly test if the remote control is working by reading the turbo rotation speed only. Run
```
python check_turbo_rpm.py
```
You will first be asked to input the USB port for the turbo.

<img width="482" height="57" alt="image" src="https://github.com/user-attachments/assets/bbd72ea7-818b-4338-b646-9da458254718" />

The port for the turbo is USBx, where x is usually a nonzero number. Here, for example, is 1. So input 1.
Then, you will be asked to choose the vacuum chamber for which the turbo is used.

<img width="520" height="73" alt="image" src="https://github.com/user-attachments/assets/57ca81de-ecaf-4b47-9cb1-7019c2caeda0" />

Type the Main or UPS. The code will then run until you interrupt it.

<img width="532" height="210" alt="image" src="https://github.com/user-attachments/assets/54f4d23f-ab6f-4649-9d7c-94fde1f98547" />

If something is wrong, you should troubleshoot the physical connection between the turbo and the Raspberry Pi. If everything is correct, you can keep going. Turn on or off the turbo, and record the turbo condition. Remember that the turbo can only receive one command at a time, so before taking the next action, end this code first.

2. To turn on the turbo, run:
```
python turbo_ON.py
```
to turn off, run:
```
python turbo_OFF.py
```

3. To record the turbo condition, e.g., its rotation speed, drive current, error codes, etc., run:
```
python check_turbo_readout.py
```
It's better to run this code in a tmux or screen session (or use nohup), so that it can keep recording the turbo condition even when you close the programming window. You will also be asked to input the USB port and choose the chamber, like what the test code check_turbo_rpm.py does.
You can monitor the turbo condition from the output in the terminal, or go to the Turbo Page on Grafana:
http://aramakilab.neu.edu:3000/d/beonjxv3kaj9ce/turbo-page?orgId=1&from=now-1h&to=now&timezone=browser&refresh=auto

If Grafana doesn't show any data, check the code check_turbo_readout.py, the turbo data in the MySQL database, and the code in Grafana. The readout data should be stored in the database first, then shown on Grafana.

