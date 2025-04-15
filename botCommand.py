import serial
import time

# Open serial port (adjust to your COM port or /dev/tty)
ser = serial.Serial('COM3', 115200)  # or '/dev/ttyUSB0' on Linux
time.sleep(2)  # Wait for GRBL to initialize

# Wake up GRBL
ser.write(b"\r\n\r\n")
time.sleep(2)
ser.flushInput()

def send_gcode(cmd):
    print(f"Sending: {cmd}")
    ser.write((cmd + '\n').encode())
    grbl_out = ser.readline().decode().strip()
    print(f"Response: {grbl_out}")
    return grbl_out

# Set to relative positioning
send_gcode("G91")

# Move to position X=20, Y=30
send_gcode("G1 X20 Y30 F500")  # F500 = feed rate

# Lower the arm (Z down = 'click')
send_gcode("G1 Z-5 F100")

# Raise the arm
send_gcode("G1 Z5 F100")

# Optionally move back
send_gcode("G1 X-20 Y-30 F500")

ser.close()
