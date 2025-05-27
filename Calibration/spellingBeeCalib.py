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

# These are the ranges that indicate the outer corner of the phone screen.
Range_X = 50
Range_Y = 30

# These values are the starting point of the phone screen.
Start_X = 10
Start_Y = 9

# This function is responsible for sending G-code commands to the GRBL controller.
def send_gcode(ser, command):
    # Since this is calibration code, we print the commands to the console for debugging.
    print(f"> {command}")
    ser.write((command + '\n').encode())
    time.sleep(0.1)
    while ser.in_waiting:
        response = ser.readline().decode().strip()
        if response:
            print(response)

# This function is responsible for getting the current position of the robot.
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
        # First, setup the serial connection to the GRBL controller.
        time.sleep(2)
        ser.write(b"\r\n\r\n")  # Wake up GRBL
        time.sleep(2)
        ser.flushInput()

        stop_flag = threading.Event()
        thread = threading.Thread(target=get_position_loop, args=(ser, stop_flag))
        thread.start()

        try:
            # Perform the calibration sequence.
            send_gcode(ser, "G90")       
            send_gcode(ser, "F1000")     
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(1)

            # This part is repeated 3 times.

            # Go to letter 6 (left up).
            send_gcode(ser, f"G0 X34 Y23")
            time.sleep(10)

            # Perform a tap.
            send_gcode(ser, f"G0 Z-0.05")
            time.sleep(0.7)
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(0.2)

            # Go to letter 7 (middle).
            send_gcode(ser, f"G0 X37 Y19")
            time.sleep(3)

            # Perform a tap.
            send_gcode(ser, f"G0 Z-0.05")
            time.sleep(0.7)
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(2)

            # Go to letter 3 (right down).
            send_gcode(ser, f"G0 X39 Y15")
            time.sleep(3)

            # Perform a tap.
            send_gcode(ser, f"G0 Z-0.05")
            time.sleep(0.7)
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(2)

            # Go to the 'enter' key.
            send_gcode(ser, f"G0 X47 Y14")
            time.sleep(3)

            # Perform a tap.
            send_gcode(ser, f"G0 Z-0.05")
            time.sleep(0.7)
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(2)

            # Repeat above sequence.

            # Go to letter 6 (left up).
            send_gcode(ser, f"G0 X34 Y23")
            time.sleep(10)

            # Perform a tap.
            send_gcode(ser, f"G0 Z-0.05")
            time.sleep(0.7)
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(0.2)

            # Go to letter 7 (middle).
            send_gcode(ser, f"G0 X37 Y19")
            time.sleep(3)

            # Perform a tap.
            send_gcode(ser, f"G0 Z-0.05")
            time.sleep(0.7)
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(2)

            # Go to letter 3 (right down).
            send_gcode(ser, f"G0 X39 Y15")
            time.sleep(3)

            # Perform a tap.
            send_gcode(ser, f"G0 Z-0.05")
            time.sleep(0.7)
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(2)

            # Go to the 'enter' key.
            send_gcode(ser, f"G0 X47 Y14")
            time.sleep(3)

            # Perform a tap.
            send_gcode(ser, f"G0 Z-0.05")
            time.sleep(0.7)
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(2)

            # Repeat above sequence.

            # Go to letter 6 (left up).
            send_gcode(ser, f"G0 X34 Y23")
            time.sleep(10)

            # Perform a tap.
            send_gcode(ser, f"G0 Z-0.05")
            time.sleep(0.7)
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(0.2)

            # Go to letter 7 (middle).
            send_gcode(ser, f"G0 X37 Y19")
            time.sleep(3)

            # Perform a tap.
            send_gcode(ser, f"G0 Z-0.05")
            time.sleep(0.7)
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(2)

            # Go to letter 3 (right down).
            send_gcode(ser, f"G0 X39 Y15")
            time.sleep(3)

            # Perform a tap.
            send_gcode(ser, f"G0 Z-0.05")
            time.sleep(0.7)
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(2)

            # Go to the 'enter' key.
            send_gcode(ser, f"G0 X47 Y14")
            time.sleep(3)

            # Perform a tap.
            send_gcode(ser, f"G0 Z-0.05")
            time.sleep(0.7)
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(2)

            # Lift the pen.
            send_gcode(ser, f"G0 Z-1")
            time.sleep(0.2)

            # Move to the home position.
            send_gcode(ser, f"G0 X0 Y0")
            time.sleep(5)

            # Move pen to start position.
            send_gcode(ser, f"G0 Z0")
            time.sleep(0.2)

        finally:
            stop_flag.set()
            thread.join()
            print("Done!")

if __name__ == "__main__":
    main()