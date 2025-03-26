import time
import serial
from serial.tools import list_ports
from lazyins import Cursor
import os
import re
import readline
import pathlib
import mysql.connector
import csv
from datetime import datetime, timedelta



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



csv_file_path = input("Please enter the dual point sensor csv file: ")

config = {
    'user': os.environ.get('LAZYINS_USER'),
    'password': os.environ.get('LAZYINS_PASSWD'),
    'host': os.environ.get('LAZYINS_HOST'),
    'port': os.environ.get('LAZYINS_PORT')
}
print(config)

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


print("Using file: ", csv_file_path, " to DATABASE ", db_name, "/", chart_name)


# Connect to MySQL
try:
    # Connect directly to the specified database
    config['database'] = db_name
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    # Create a set to track existing timestamps
    cursor.execute(f"SELECT time FROM `{chart_name}`")
    existing_timestamps = {row[0] for row in cursor.fetchall()}
    
    # Read and process CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, quotechar='"', delimiter=',', quoting=csv.QUOTE_MINIMAL)
        next(reader)  # Skip header row
        
        insert_query = f"""
        INSERT INTO `{chart_name}` 
        (time, Temperature_Celsius, Relative_Humidity, DPT, VPD, Abs_Humidity)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        row_count = 0
        duplicate_count = 0
        
        for row in reader:
            if len(row) >= 6:
                try:
                    # Parse and convert to UTC
                    date_obj = datetime.strptime(row[0].strip(), '%m/%d/%y %H:%M')
                    date_obj = date_obj - timedelta(hours=5)  # UTC conversion
                    
                    # Skip if timestamp already exists
                    if date_obj in existing_timestamps:
                        duplicate_count += 1
                        continue
                        
                    # Convert values
                    temperature = float(row[1])
                    humidity = float(row[2])
                    dpt = float(row[3])
                    vpd = float(row[4])
                    abs_humidity = float(row[5])
                    
                    cursor.execute(insert_query, (
                        date_obj,
                        temperature,
                        humidity,
                        dpt,
                        vpd,
                        abs_humidity
                    ))
                    
                    # Add to existing timestamps set
                    existing_timestamps.add(date_obj)
                    row_count += 1
                    
                    if row_count % 100 == 0:
                        conn.commit()
                        
                except ValueError as e:
                    print(f"Skipping row due to error: {e}")
                    continue
    
    conn.commit()
    print(f"Successfully imported {row_count} new rows into `{db_name}`.`{chart_name}`")
    print(f"Skipped {duplicate_count} duplicate timestamp entries")
    
except mysql.connector.Error as err:
    print(f"Database error: {err}")
except Exception as e:
    print(f"Error: {e}")
    if 'conn' in locals():
        conn.rollback()
    
finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()