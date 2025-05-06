import serial
import time
import threading
import keyboard  # For arrow key input

# Set your serial port and baud rate
SERIAL_PORT = '/dev/tty.usbmodem14201'  # <-- Replace with your actual port
BAUD_RATE = 115200

# GRBL max travel values (match your $130, $131, $132)
MAX_X = 110
MAX_Y = 120
MAX_Z = 50

# Range used for motion
Range_X = 55
Range_Y = 30

Start_X = 10
Start_Y = 9

# Jog step in mm
JOG_STEP = 0.25

# Current position (updated manually)
current_x = 50
current_y = 11.75
current_z = 0

def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))

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

def handle_keypress(ser):
    global current_x, current_y, current_z

    if keyboard.is_pressed("left"):
        current_y = clamp(current_y - JOG_STEP, 0, Range_Y)
        send_gcode(ser, f"G0 Y{current_y}")
        time.sleep(0.1)

    elif keyboard.is_pressed("right"):
        current_y = clamp(current_y + JOG_STEP, 0, Range_Y)
        send_gcode(ser, f"G0 Y{current_y}")
        time.sleep(0.1)

    elif keyboard.is_pressed("up"):
        current_x = clamp(current_x + JOG_STEP, 0, Range_X)
        send_gcode(ser, f"G0 X{current_x}")
        time.sleep(0.2)

    elif keyboard.is_pressed("down"):
        current_x = clamp(current_x - JOG_STEP, 0, Range_X)
        send_gcode(ser, f"G0 X{current_x}")
        time.sleep(0.2)

    elif keyboard.is_pressed("t"):
        print("Current: ", current_x, current_y, current_z)
        current_z = -0.05
        send_gcode(ser, f"G0 Z{current_z}")
        time.sleep(0.2)
        current_z = -0.4
        send_gcode(ser, f"G0 Z{current_z}")
        time.sleep(0.2)
    
    elif keyboard.is_pressed("u"):
        current_z = -0.4
        send_gcode(ser, f"G0 Z{current_z}")
        time.sleep(0.2)
    
    elif keyboard.is_pressed("h"):
        send_gcode(ser, f"G0 X0 Y0")
        time.sleep(5)
        send_gcode(ser, f"G0 Z0")
        time.sleep(0.5)

def main():
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        time.sleep(2)
        ser.write(b"\r\n\r\n")  # Wake up GRBL
        time.sleep(2)
        ser.flushInput()
        current_x = 34
        current_y = 23

        # stop_flag = threading.Event()
        # thread = threading.Thread(target=get_position_loop, args=(ser, stop_flag))
        # thread.start()
        

        try:
            send_gcode(ser, "G90")         # Absolute positioning
            send_gcode(ser, "F1000")       # Feedrate (mm/min)

            # send_gcode(ser, f"G0 X{current_x} Y{current_y} Z{current_z}")
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(1)

            # Go to middle letter.
            send_gcode(ser, f"G0 X50 Y11.75")
            current_x = 34
            current_y = 23
            time.sleep(5)

            print("Use ← → ↑ ↓ to move, T to change Z, ESC to quit.")

            while True:
                handle_keypress(ser)
                # print(f"Current Position: X={current_x}, Y={current_y}, Z={current_z}")
                if keyboard.is_pressed("esc"):
                    break
                time.sleep(0.2)

        finally:
            # stop_flag.set()
            # thread.join()
            print("Exiting...")

if __name__ == "__main__":
    main()
