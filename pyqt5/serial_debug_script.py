import serial
import time
from serial.tools import list_ports

def test_serial_port(port_path, commands):
    """Test a serial port with different commands and settings"""
    print(f"\n=== Testing {port_path} ===")
    
    # Common baud rates to try
    baud_rates = [9600, 19200, 38400, 57600, 115200]
    
    for baud in baud_rates:
        print(f"\nTrying baud rate: {baud}")
        try:
            # Open serial connection
            ser = serial.Serial(
                port_path,
                baudrate=baud,
                parity='N',
                stopbits=1,
                bytesize=8,
                timeout=2
            )
            
            # Clear buffers
            ser.flushInput()
            ser.flushOutput()
            time.sleep(0.1)
            
            # Test each command
            for cmd_name, command in commands.items():
                print(f"  Testing command '{cmd_name}': {command}")
                
                # Send command
                ser.write(command.encode('ascii'))
                time.sleep(1)  # Wait for response
                
                # Try to read response
                response = ser.read(100)
                if response:
                    print(f"    ✓ Response: {response}")
                    print(f"    ✓ Decoded: {repr(response.decode('ascii', errors='ignore'))}")
                    ser.close()
                    return port_path, baud, cmd_name, response
                else:
                    print(f"    ✗ No response")
            
            ser.close()
            
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    return None

def main():
    # Get available ports
    ports = [info.device for info in list_ports.comports()]
    print("Available serial ports:", ports)
    
    # Commands to test (based on your original code)
    test_commands = {
        'original_hardcoded': '0010030902=?107\r',
        'calculated_checksum': '0000030902=?106\r',
        'simple_query': '*IDN?\r',
        'basic_status': '?\r',
        'address_001': '0010030902=?107\r',
        'pressure_cmd': '$PRA95F7\r'
    }
    
    print("\nTesting all available ports with different commands...")
    
    working_configs = []
    
    # Test each port
    for port in ports:
        result = test_serial_port(port, test_commands)
        if result:
            working_configs.append(result)
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY:")
    if working_configs:
        print("✓ Found working configurations:")
        for port, baud, cmd, response in working_configs:
            print(f"  Port: {port}, Baud: {baud}, Command: {cmd}")
            print(f"  Response: {response}")
    else:
        print("✗ No working configurations found")
        print("\nTroubleshooting suggestions:")
        print("1. Check if the device is powered on and connected")
        print("2. Verify the correct serial port (try unplugging/plugging device)")
        print("3. Check device documentation for correct command format")
        print("4. Try different baud rates or connection settings")
        print("5. Use a serial monitor tool to test manually")

if __name__ == "__main__":
    main()