import time
import serial
from serial.tools import list_ports
from lazyins import Cursor
import os
import re
import readline
import pathlib
import mysql.connector
from datetime import datetime
import pandas as pd



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

try:
    config = {
        'user': os.environ.get('LAZYINS_USER'),
        'password': os.environ.get('LAZYINS_PASSWD'),
        'host': os.environ.get('LAZYINS_HOST'),
        'port': os.environ.get('LAZYINS_PORT')
    }
    if None in config.values():
        raise ValueError("One or more environment variables are missing.")
except:
    print("Your system variables are not correctly set, checkout instructions on https://github.com/Eclipsedclaw/ALAB_housekeeping/tree/main/MKS_gauge\n")
    print("Please manually put the information for mysql database\n")
    mysql_host = input("Please manually input mysql host name: ")
    mysql_port = 3306
    mysql_port = input("Please manually input mysql port(defualt 3306): ")
    mysql_username = input("Please manually input mysql username: ")
    mysql_passwd = input("Please manually input mysql password: ")
    config = {
        'user': mysql_username,
        'password': mysql_passwd,
        'host': mysql_host,
        'port': mysql_port
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

# Define your time range
start_time = input("Enter the start time that you want to export(format with year-month-date hr:min:sec, 2024-08-16 14:12:00): ")
end_time = input("Enter the end time that you want to export(format with year-month-date hr:min:sec, 2024-08-16 14:12:00): ")
save_path = input("Enter full path for saved csv file:")

# SQL query to select data within the specified time range
query = f"""
SELECT *
FROM CPS_testing
WHERE time BETWEEN '{start_time}' AND '{end_time}';
"""

print("Query data from ", db_name, "/", chart_name, " to file", save_path)

# Create the directory if it doesn't exist
os.makedirs(save_path, exist_ok=True)

# Define the Excel file path with the specific directory and current date and time
output_file = os.path.join(save_path, f"CPS_testing_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")

# Fetch data and export to Excel
try:
    # Execute the query and load data into a pandas DataFrame
    df = pd.read_sql(query, connection)
    
    # Export DataFrame to Excel
    df.to_excel(output_file, index=False)
    
    print(f"Data successfully exported to {output_file}")
finally:
    # Close the database connection
    connection.close()



cursor.close()
connection.close()