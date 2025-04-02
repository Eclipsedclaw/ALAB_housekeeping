import time
import serial
from serial.tools import list_ports
from lazyins import Cursor
import os
import re
import readline
import pathlib
import mysql.connector
import math

def convert_RTD_ADC(x, offset):
    try:
        # Validate input x
        x_float = float(x)
    except ValueError:
        print("Error: Input 'x' is not a valid numeric value.")
        return None

    try:
        # Validate input offset
        offset_float = float(offset)
    except ValueError:
        print("Error: Input 'offset' is not a valid numeric value.")
        return None

    # Perform the calculations
    try:
        # In lab we are using 3.3V as board power supply thes none of the ADC could exceed 2715
        L_V = x_float * (3.3 / 2715.0)
        if(x>=2715):
            print("Open circuit!")
            return None
        else:
            L_R = L_V * 1000. / (3.3 - L_V)
            L_tmp = -(math.sqrt(17.59246 - 0.00232 * L_R) - 3.908) / 0.00116
            L_tmpK = L_tmp + 273.15
            L_correction = L_tmpK + offset_float  # No correction for now
            if L_correction > 73:
                return round(float(L_correction), 2)    # Round to 2 digits
            else:
                return None
    except Exception as e:
        print(f"Error during data querying")
        return None


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

# search serial port
ser = serial.Serial()
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)

port = input("Please enter the MHADC board port: ")

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


print("Send data to DATABASE ", db_name, "/", chart_name)

# TODO: make baud_rate user input available
baud_rate = 9600
# TODO: Current only take readout command a, if we have further comamnd, need to implement here
command = "a"


max_retries = 100  # Maximum number of retries
retry_delay = 20   # Delay between retries in seconds

for attempt in range(max_retries):

    try:
        while True:
            ser = serial.Serial(port, baud_rate)
            ser.write(command.encode())

            response = ser.readline().decode().strip()
            print("raw readout is: ", response)
            chunks = response.split('_')

            values = [int(chunks[i]) for i in range(1, len(chunks), 2)]
            offset = [-2, -4, -2, -5, -4, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            # channel definition, currently 1 means temperature sensor that need conversion, 0 means raw digital output
            channel_def = [1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            hubADC_output = []
            for n in range(len(values)):
                if channel_def[n]==1:
                    hubADC_output.append(convert_RTD_ADC(values[n], offset[n]))
                if channel_def[n]==0:
                    hubADC_output.append(values[n])


            # MHADC 32 channels
            ADCchannel_name = [f"Ch{i+1}" for i in range(len(hubADC_output))]
            ADCchannel_type = ["float" if ch_def == 1 else "int" for ch_def in channel_def]
            # insert
            cursor = Cursor(host=os.environ.get('LAZYINS_HOST'), port=os.environ.get('LAZYINS_PORT'), user=os.environ.get('LAZYINS_USER'), passwd=os.environ.get('LAZYINS_PASSWD'), db_name = db_name, table_name = chart_name)
            if(all(element is None for element in hubADC_output)):
                print("ALL MKS readout shows NONE! Check communication connection!")
            else:
                cursor.setup(ADCchannel_name, types = ADCchannel_type)
                cursor.register(hubADC_output)
                print("\nreadout MHADC as: ", hubADC_output)
            time.sleep(1)  # Delay for 0.1 second
    except Exception as e:
        print(f"Attempt {attempt + 1} failed: {str(e)}")
        if attempt == max_retries - 1:
            raise  # Re-raise the last exception if all retries failed
        time.sleep(retry_delay)
