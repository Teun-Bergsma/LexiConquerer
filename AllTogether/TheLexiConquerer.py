import serial
import time
import random
import threading
import sys
import keyboard
from GameHandler.Wordle import Wordle
from GameHandler.SpellingBee import SpellingBee
# Important: make sure to install the scrcpy (https://github.com/Genymobile/scrcpy) on your system, otherwise this will not run.
# Phone needs to be connected to the computer and USB debugging enabled.
# from ppadb.client import Client as AdbClient
from PIL import Image
from enum import Enum
from typing import List

# Set your serial port and baud rate here
SERIAL_PORT = '/dev/tty.usbmodem14101'  # <-- Replace with your actual port!
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

# Connect both the the phone usb port and the grbl port
def connectPorts():
    print("Connecting to the phone...")
    print("TODO")
    print("Connecting to the grbl...")
    print("TODO")
    print("Connected to both the phone and grbl.")

def get_screen_tap_locations(gametype):
    # Spelling Beem Game, return locations of the 7 letters in a format of letter, x, y
    if gametype == "1":
        return [
            ('letter1', 32, 19),
            ('letter2', 34, 15),
            ('letter3', 39, 15),
            ('letter4', 42, 19),
            ('letter5', 39, 23),
            ('letter6', 34, 23),
            ('letter7', 37, 19),
            ('enter', 47, 14),
            # ('back', 900, 200)
        ]
    # Wordle Game, return locations of the 26 letters, the enter and the back keys in a format of letter, x, y
    elif gametype == "2":
        return [
            ('a', 48.5, 27),
            ('b', 52, 16.25),
            ('c', 52, 20.5),
            ('d', 48.5, 22.5),
            ('e', 44.75, 23.75),
            ('f', 48.5, 20.5),
            ('g', 48.5, 18.25),
            ('h', 48.5, 16.25),
            ('i', 44.75, 13),
            ('j', 48.5, 14),
            ('k', 48.5, 11.75),
            ('l', 48.5, 9.5),
            ('m', 52, 12),
            ('n', 52, 14.25),
            ('o', 44.75, 11),
            ('p', 44.75, 9),
            ('q', 44.75, 28.25),
            ('r', 44.75, 21.5),
            ('s', 48.5, 24.75),
            ('t', 44.75, 19.25),
            ('u', 44.75, 15.25),
            ('v', 52, 18.5),
            ('w', 44.75, 26),
            ('x', 52, 22.75),
            ('y', 44.75, 17.25),
            ('z', 52, 25),
            ('enter', 52.5, 27.5),
            ('back', 2800, 200)
        ]
    else:
        print("Invalid game type. Please choose 1 for Spelling Bee or 2 for Wordle.")
        return []

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
        # Check if the user provided an argument
        if len(sys.argv) < 2:
            print("Usage: python TheLexiConquerer.py [game_type_number]")
            print("Example: python TheLexiConquerer.py 1")
            sys.exit(1)

        connectPorts()
        game_type_arg = sys.argv[1]
        screen_tap_locations = get_screen_tap_locations(game_type_arg)

        # Spelling Bee Game
        if game_type_arg == "1":
            # Start robot:
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(0.2)
            x_middle = screen_tap_locations[6][1]
            y_middle = screen_tap_locations[6][2]
            send_gcode(ser, f"G0 X{x_middle} Y{y_middle}")
            time.sleep(10)


            valid_letters = ['i', 'w', 'b', 'l', 'o', 'e', 'p']
            required_letter = 'p'
            # Update the first item (the letter) by creating a NEW tuple
            for i in range(len(valid_letters)):
                letter, x, y = screen_tap_locations[i]  # unpack
                screen_tap_locations[i] = (valid_letters[i], x, y)  # create a new tuple

            print(screen_tap_locations)

            spelling_bee = SpellingBee(valid_letters, required_letter)
            valid_words = spelling_bee.find_valid_words()

            print(f"Found {len(valid_words)} valid words:")
            shuffled_list = random.shuffle(valid_words)
            shuffled_list = valid_words.copy()
            random.shuffle(shuffled_list)
            sorted_list = sorted(shuffled_list, key=len, reverse=True)
            # print(f"Shuffled list: {shuffled_list}", type(shuffled_list))
            for word in sorted_list:
                print(word)
                # Loop through the letters of the word and tap on the screen
                for letter in word:
                    # Find the corresponding screen tap location
                    for loc in screen_tap_locations:
                        if loc[0] == letter:
                            x, y = loc[1], loc[2]
                            print(f"Tapping on {letter} at ({x}, {y})")
                            send_gcode(ser, f"G0 X{x} Y{y}")
                            time.sleep(2)
                            send_gcode(ser, f"G0 Z-0.05")
                            time.sleep(0.5)
                            send_gcode(ser, f"G0 Z-0.4")
                            time.sleep(0.2)
                            # Simulate a tap on the screen at (x, y)
                print("Tapping on enter")
                x = screen_tap_locations[7][1]
                y = screen_tap_locations[7][2]
                send_gcode(ser, f"G0 X{x} Y{y}")
                time.sleep(2)
                send_gcode(ser, f"G0 Z-0.05")
                time.sleep(0.5)
                send_gcode(ser, f"G0 Z-0.4")
                time.sleep(0.2)
                send_gcode(ser, f"G0 X{x_middle} Y{y_middle}")
                time.sleep(5)
                if keyboard.is_pressed("esc"):
                    send_gcode(ser, f"G0 X0 Y0")
                    time.sleep(10)
                    send_gcode(ser, f"G0 Z0")
                    time.sleep(0.5)
                    exit()
                # Simulate a tap on the enter key
        
        elif game_type_arg == "2":
            print("Wordle Game")
            wordle = Wordle()
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(0.2)
            x_middle = screen_tap_locations[6][1]
            y_middle = screen_tap_locations[6][2]
            send_gcode(ser, f"G0 X{x_middle} Y{y_middle}")
            time.sleep(10)

            # Simulate making guesses and getting feedback
            for attempt in range(wordle.max_attempts):
                if attempt == 0:
                    guess = "furor"
                else:
                    guess = wordle.make_guess()
                if guess is None:
                    print("No valid guesses left!")
                    break
                # input("Press 'Y' and Enter to continue: ").strip().upper() != 'Y' and exit("Exiting game.")
                print(f"Guessing: {guess}")
                # print(word)
                # Loop through the letters of the word and tap on the screen
                for letter in guess:
                    # Find the corresponding screen tap location
                    for loc in screen_tap_locations:
                        if loc[0] == letter:
                            x, y = loc[1], loc[2]
                            print(f"Tapping on {letter} at ({x}, {y})")
                            send_gcode(ser, f"G0 X{x} Y{y}")
                            time.sleep(2)
                            send_gcode(ser, f"G0 Z-0.05")
                            time.sleep(0.5)
                            send_gcode(ser, f"G0 Z-0.4")
                            time.sleep(0.2)
                            # Simulate a tap on the screen at (x, y)
                print("Tapping on enter")
                x = screen_tap_locations[26][1]
                y = screen_tap_locations[26][2]
                send_gcode(ser, f"G0 X{x} Y{y}")
                time.sleep(2)
                send_gcode(ser, f"G0 Z-0.05")
                time.sleep(0.5)
                send_gcode(ser, f"G0 Z-0.4")
                time.sleep(0.2)
                send_gcode(ser, f"G0 X{x_middle} Y{y_middle}")
                time.sleep(5)
                if keyboard.is_pressed("esc"):
                    send_gcode(ser, f"G0 X0 Y0")
                    time.sleep(10)
                    send_gcode(ser, f"G0 Z0")
                    time.sleep(0.5)
                    exit()
                # Simulate a tap on the enter key
                is_correct = wordle.update_info(guess, attempt)
                if is_correct:
                    print(f"Correct guess! The word was '{guess}'")
                    send_gcode(ser, f"G0 X0 Y0")
                    time.sleep(10)
                    send_gcode(ser, f"G0 Z0")
                    time.sleep(0.5)
                    break

                print(f"Attempt {attempt + 1}/{wordle.max_attempts} failed.\n")


if __name__ == "__main__":
    main()