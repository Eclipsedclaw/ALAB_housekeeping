# How to run the turbo codes
1. First of all, check and connect to an existing tmux or screen session for the turbo that needs to be operated. If there aren't any, start a new tmux or screen session for the turbo.

2. **Turbo Readout**:

In the tmux or screen session, if there are currently normal turbo outputs looking like the figure below, and the turbo data is already shown on Grafana, then the turbo readout is working properly. Skip to the next step if the turbo needs to be turned on/off. Otherwise, in the current tmux or screen session, run
```
python check_turbo_readout.py
```
You will first be asked to input the USB port for the turbo. The port for the turbo is USBx, where x is usually a nonzero number. Here, for example, is 2. So input 2.

<img width="468" height="106" alt="image" src="https://github.com/user-attachments/assets/9828ecd5-d318-4f59-a735-33a88f942f14" />

Then, you will be asked to choose the vacuum chamber for which the turbo is used. Type "Main" or "UPS". The code will then run until you interrupt it.

<img width="468" height="363" alt="image" src="https://github.com/user-attachments/assets/5f53086c-8027-4cdc-abe2-739e9f384d21" />

If something is wrong, you should troubleshoot the physical connection between the turbo and the Raspberry Pi. If everything is correct, you can keep going. Turn on or off the turbo, and record the turbo condition. Remember that the turbo can only receive one command at a time, so before taking the next action, end this code first.

3. **Turbo Control**:

To turn on or turn off the turbo, interrupt any running turbo readout script first. Then, to turn on, run:
```
python turbo_ON.py
```

<img width="468" height="127" alt="image" src="https://github.com/user-attachments/assets/b10dae7c-98ae-4ca2-8e55-7586ae556a75" />

to turn off, run:
```
python turbo_OFF.py
```

<img width="464" height="129" alt="image" src="https://github.com/user-attachments/assets/9e43c7b2-0ae9-4b51-a526-ce94a83b976a" />

After turning on/off the turbo, it's supposed to monitor the turbo status immediately. That said, to record the turbo condition in the database, e.g., its rotation speed, drive current, error codes, etc. Again, run:
```
python check_turbo_readout.py
```
You can monitor the turbo condition from the output in the terminal, or go to the Turbo Page on Grafana:
http://aramakilab.neu.edu:3000/d/beonjxv3kaj9ce/turbo-page?orgId=1&from=now-1h&to=now&timezone=browser&refresh=auto

If Grafana doesn't show any data, check the code check_turbo_readout.py, the turbo data in the MySQL database, and the code in Grafana. The readout data should be stored in the database first, then shown on Grafana.


