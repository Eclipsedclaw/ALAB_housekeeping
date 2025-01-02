import time
import serial
from serial.tools import list_ports
from lazyins import Cursor
import os
import re
import readline
import pathlib
import mysql.connector



def complete_path(text, state):
    incomplete_path = pathlib.Path(text)
    if incomplete_path.is_dir():
        completions = [p.as_posix() for p in incomplete_path.iterdir()]
    elif incomplete_path.exists():
        completions = [incomplete_path]
    else:
        exists_parts = pathlib.Path('.')
        for part in incomplete_path.parts:
            test_next_part = exists_parts / part
            if test_next_part.exists():
                exists_parts = test_next_part

        completions = []
        for p in exists_parts.iterdir():
            p_str = p.as_posix()
            if p_str.startswith(text):
                completions.append(p_str)
    return completions[state]


# we want to treat '/' as part of a word, so override the delimiters
readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete_path)
#print(input('tab complete a filename: '))

def pump_data(serial_path,  db_name, table_name, MKS_address, serial_baudrate = 115200, serial_parity = 'N', serial_stopbits = 1, serial_bytesize = 8):
    while True:
        MKS = serial.Serial(serial_path)
        MKS.baudrate = serial_baudrate
        MKS.parity = serial_parity
        MKS.stopbits = serial_stopbits
        MKS.bytesize = serial_bytesize

        print("Getting pressure data now...")
        #host=os.environ.get('LAZYINS_HOST')
        #print("host is: "+str(host))

        try:
            cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = db_name, table_name = table_name)
            
            # table for pressure in db
            name_pressure = ['PR1', 'PR2', 'PR3', 'PR4', 'PR5']
            types_pressure = ['float', 'float', 'float', 'float', 'float']
            chamber_pressure = []
            for i in range(5):
                command = "@"+str(MKS_address)+"PR"+str(i+1)+"?;FF"
                MKS.write((command).encode('utf8'))
                time.sleep(0.1)
                try:
                    ChamberPressureOut = MKS.read(MKS.inWaiting()).decode('utf8')
                    print("ChamberPressureOut for PR"+str(i+1)+" string is: "+ str(ChamberPressureOut))
                    try:
                        match = re.search(fr'@{MKS_address}ACK(.*?)\;FF', ChamberPressureOut)
                        chamber_pressure.append(abs(float(match.group(1))))
                    except Exception as e:
                        print("Error for readout PR"+str(i+1)+"!")
                        chamber_pressure.append(0)
                except Exception as e:
                    print("Error in chamber pressure query:", e)
                finally:
                    print("")
                time.sleep(0.1)

            # Ensure the port is closed properly
            MKS.close()
            values_pressure = chamber_pressure
            print(values_pressure)

            # insert
            cursor.setup(name_pressure, types = types_pressure)
            cursor.register(values_pressure)

            print("Current pressure: ", values_pressure)
            return values_pressure
        except Exception as e:
            print("Error in pressure query:", e)
            pass
            return None


def MKS_serial_command(MKS_command, serial_path, serial_baudrate = 115200, serial_parity = 'N', serial_stopbits = 1, serial_bytesize = 8):
    while True:
        MKS = serial.Serial(serial_path)
        MKS.baudrate = serial_baudrate
        MKS.parity = serial_parity
        MKS.stopbits = serial_stopbits
        MKS.bytesize = serial_bytesize

        print("You are sending command: ", MKS_command, " to device: ", serial_path)
        MKS.write((MKS_command).encode('utf-8'))
        time.sleep(0.1)
        
        readout = MKS.read(MKS.inWaiting())
        print("serial output is: ", readout)

        serial_out = readout.decode('utf-8')

        print("serial output after utf-8 decode is: ",serial_out)
        MKS.close()
        return serial_out
    #except Exception as e:
    #    print("Error in MKS serial communication:", e)
    #    return None


# search serial port
ser = serial.Serial()
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)

port_path = input("Please enter the data port: ")
print("MKS gauge port address serial reply:")
MKS_serial_command(MKS_command='@254AD?;FF', serial_path=port_path, serial_baudrate = 115200, serial_parity = 'N', serial_stopbits = 1, serial_bytesize = 8)

MKS_address = input("Please enter MKS gauge address: ")


config = {
    'user': os.environ.get('LAZYINS_USER'),
    'password': os.environ.get('LAZYINS_PASSWD'),
    'host': os.environ.get('LAZYINS_HOST'),
    'port': os.environ.get('LAZYINS_PORT')
}

# Get database name from user input
connection = mysql.connector.connect(**config)
cursor = connection.cursor()
cursor.execute("SHOW DATABASES")
databases = cursor.fetchall()
print("Databases available:")
for db in databases:
    print(f" - {db[0]}")

db_name = input("Please enter the database that you want to use: ")

cursor.execute(f"USE {db_name}")

# Get table name (chart name) from user input
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print(f"Tables in database '{db_name}':")
for table in tables:
    print(f" - {table[0]}")
chart_name = input("Please enter the chart (table) name that you want to pump data to: ")


cursor.close()
connection.close()


print("Query data from ", port_path, " to DATABASE ", db_name, "/", chart_name)

try:
    while True:
        pump_data(serial_path=port_path, MKS_address=MKS_address, db_name=db_name, table_name=chart_name)
        time.sleep(1)  # Delay for 0.1 second
except KeyboardInterrupt:
    print("Process interrupted by the user.")
