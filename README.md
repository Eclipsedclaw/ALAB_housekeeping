### To use script that directly pump MKS pressure gauge data to database, go to MKS_gauge
```bash
cd ./MKS_gauge/
```

### To use pyQt5 python GUI, go to pyqt5
```bash
cd ./pyqt5/
```

### To use python GUI, go to Python_UI
```bash
cd ./Python_UI/
```

### To import DP sensor csv files to mysql database, go to DPsensor
```bash
cd ./DPsensor/
```

<h2>How to pipe data from devices to grafana (MKS gauge, RTDs via MHADC board, turbo control)</h2>
Quick note: The following scripts should ideally be run using screen/tmux so that data piping does not stop once the ssh session is terminated.
You can create a screen by running 
```
screen -S screen_name
```

You can see which screens are active by running
```screen -ls```

You can reattach to a previous screen by running
```screen -r screen_name```

You can detach from an existing screen by using the Ctrl+A+D keyboard shortcut (yes, Ctrl, even on macOS)

<h3>MKS Gauge</h3>
First, ssh into the pi. Ask one of the grad students for the IP address. Navigate to the
```ALAB_housekeeping/MKS_gauge``` folder. Then, run the following command.
```python3 MKS2database.py```

This will prompt you for a port and a gauge address. The port can be found by trial and error. The gauge address is currently 001. 
The correct database to pipe to is ```bench_test```. The correct table is ```CPS_testing```.

<h3>RTDs vis MHADC board</h3>
After you ssh into the pi, go to ```ALAB_housekeeping/MHADC```. Run the script using the following command.
```python3 MHADC2database.py```

This will also prompt you for a port; use trial and error to figure this out. The database should be ```bench_test``` and the table should be ```MHADC```.

<h3>Turbo control</h3>
After you ssh into the pi, go to ```ALAB_housekeeping/pyqt5```. Run the script for full turbo readout using the following command.
```python3 check_turbo_readout.py```
