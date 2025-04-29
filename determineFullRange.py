import serial
import time
import threading

# Set your serial port and baud rate here
SERIAL_PORT = '/dev/tty.usbmodem14201'  # <-- Replace with your actual port!
BAUD_RATE = 115200

# Define GRBL max travel values (match your $130, $131, $132 settings)
MAX_X = 110  # 395 mm PHYSICAL LIMIT 
MAX_Y = 120  # 420 mm PHYSICAL LIMIT
MAX_Z = 50   # mm

# We use max ranges:
# Range_X = 55
# Range_Y = 30

Range_X = 50
Range_Y = 30

Start_X = 10
Start_Y = 9

def send_gcode(ser, command):
    print(f"> {command}")
    ser.write((command + '\n').encode())
    time.sleep(0.1)
    while ser.in_waiting:
        response = ser.readline().decode().strip()
        if response:
            print(response)

def get_position_loop(ser, stop_flag):
    while not stop_flag.is_set():
        ser.write(b'?\n')
        time.sleep(0.1)
        while ser.in_waiting:
            response = ser.readline().decode().strip()
            if response.startswith('<'):
                print(f"[POS] {response}")
        time.sleep(1)

def main():
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        time.sleep(2)
        ser.write(b"\r\n\r\n")  # Wake up GRBL
        time.sleep(2)
        ser.flushInput()

        stop_flag = threading.Event()
        thread = threading.Thread(target=get_position_loop, args=(ser, stop_flag))
        thread.start()

        try:
            send_gcode(ser, "G90")         # Absolute positioning
            send_gcode(ser, "F1000")       # Feedrate (mm/min)
            send_gcode(ser, f"G0 Z-1")
            time.sleep(1)
            send_gcode(ser, f"G0 X{Range_X} Y{Range_Y}")
            time.sleep(10)

            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(5)

            send_gcode(ser, f"G0 Z-0.1")
            time.sleep(5)

            send_gcode(ser, f"G0 Z-1")
            time.sleep(5)
            send_gcode(ser, f"G0 X{Start_X} Y{Start_Y}")
            time.sleep(5)
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(5)
            send_gcode(ser, f"G0 Z-0.2")
            time.sleep(5)
            send_gcode(ser, f"G0 Z-0.6")
            time.sleep(5)

            # Then Y max (no homing, just move directly to max Y)
            # send_gcode(ser, f"G0 Y{Range_Y}")
            # time.sleep(10)
            # send_gcode(ser, "Z0")
            # time.sleep(3)
            # Optionally: return to origin (no homing, just set positions)
            send_gcode(ser, "G0 X0 Y0 Z0")
            time.sleep(10)

        finally:
            stop_flag.set()
            thread.join()
            print("Done!")

if __name__ == "__main__":
    main()