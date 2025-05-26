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

from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # Perform `export [API KEY]` in the terminal. A working API key can be found in the README.
)

# Set your serial port and baud rate here
SERIAL_PORT = '/dev/tty.usbmodem14201'  # <-- Replace with your actual port!
BAUD_RATE = 115200

# Define GRBL max travel values (match your $130, $131, $132 settings)
MAX_X = 110  # 395 mm PHYSICAL LIMIT 
MAX_Y = 120  # 420 mm PHYSICAL LIMIT
MAX_Z = 50   # mm

# These are the used ranges that indicate the outer corner of the phone screen.
Range_X = 50
Range_Y = 30 

def get_screen_tap_locations(gametype):
    # Spelling Bee Game, return locations of the 7 letters in a format of letter, x, y.
    # We do not use the back key.
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
    # Wordle Game, return locations of the 26 letters, the enter and the back keys in a format of letter, x, y.
    # We dot not use the back key.
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

# This function is responsible for sending G-code commands to the GRBL controller.
def send_gcode(ser, command):
    ser.write((command + '\n').encode())
    time.sleep(0.1)
    while ser.in_waiting:
        response = ser.readline().decode().strip()

# This function is responsible for getting the current position of the robot.
def get_position_loop(ser, stop_flag):
    while not stop_flag.is_set():
        ser.write(b'?\n')
        time.sleep(1)

def main():
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        # First, setup the serial connection to the GRBL controller.
        time.sleep(2)
        ser.write(b"\r\n\r\n")  # Wake up GRBL
        time.sleep(2)
        ser.flushInput()
        # Check if the user provided an argument
        if len(sys.argv) < 2:
            print("Usage: python TheLexiConquerer.py [game_type_number]")
            print("Example: python TheLexiConquerer.py 1")
            sys.exit(1)

        print("Connected to both the phone and grbl.")
        game_type_arg = sys.argv[1] # Get the game type.
        screen_tap_locations = get_screen_tap_locations(game_type_arg) # Get the corresponding screen tap locations.

        # Spelling Bee Game
        if game_type_arg == "1":
            CHATGPTTOGGLE = False # Toggle to use the ChatGPT implementation or not.
            # Start robot:
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(0.2)
            # Move to the middle of the phone screen.
            x_middle = screen_tap_locations[6][1]
            y_middle = screen_tap_locations[6][2]
            send_gcode(ser, f"G0 X{x_middle} Y{y_middle}")
            time.sleep(10)

            # Define the valid letters and the required letter for the Spelling Bee game.
            # Manually change this!
            valid_letters = ['t', 'n', 'a', 'i', 'l', 'o', 'y']
            required_letter = 'y'
            # Update the first item (the letter) by creating a NEW tuple
            for i in range(len(valid_letters)):
                letter, x, y = screen_tap_locations[i]  # Unpack
                screen_tap_locations[i] = (valid_letters[i], x, y)  # Create a new tuple

            # Create an instance of the SpellingBee class with the valid letters and required letter.
            spelling_bee = SpellingBee(valid_letters, required_letter)
            if not CHATGPTTOGGLE: # Classical approach.
                # Get the list of words from the Spelling Bee Word List.
                # Sort this list by length.
                valid_words = spelling_bee.find_valid_words()
                print(f"Found {len(valid_words)} valid words:")
                shuffled_list = random.shuffle(valid_words)
                shuffled_list = valid_words.copy()
                random.shuffle(shuffled_list)
                sorted_list = sorted(shuffled_list, key=len, reverse=True)
            else: # ChatGPT aproach.
                # Get the list of words from ChatGPT
                # Cnstruct prompt.
                inputstr = f"Please give me a list of about 50 words that can be formed with the letters {valid_letters} and that contain the letter {required_letter}. The words should be in lowercase and separated by commas. NO OTHER LETTERS THAN THE ONES MENTIONED MAY BE USED! DO NOT GIVE DUPLICATE WORDS! Do not write any prior texts such as 'this is what you can provide...'. I want ONLY what I described."
                print("prompt: ", inputstr)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": inputstr}
                    ],
                    temperature=0,
                    max_tokens=1000,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0,
                )
                # Parse the response to get the list of words.
                # Get the unique, valid words from the response. Those are used as input words.
                # Also sort the list by length.
                word_list = response.choices[0].message.content.split(",")
                word_list = [word.strip() for word in word_list]
                print(f"Found {len(word_list)} valid words:")
                unique_words = set(word_list)
                valid_words = [word for word in unique_words if spelling_bee.is_valid_word(word)]
                shuffled_list = valid_words.copy()
                random.shuffle(shuffled_list)
                sorted_list = sorted(shuffled_list, key=len, reverse=True)
            for word in sorted_list:
                print(word)
                # Loop through the letters of the word and tap on the screen
                for letter in word:
                    # Find the corresponding screen tap location
                    for loc in screen_tap_locations:
                        if loc[0] == letter:
                            # Simulate a tap on the screen at (x, y)
                            x, y = loc[1], loc[2]
                            print(f"Tapping on {letter} at ({x}, {y})")
                            send_gcode(ser, f"G0 X{x} Y{y}")
                            time.sleep(2)
                            send_gcode(ser, f"G0 Z-0.05")
                            time.sleep(0.5)
                            send_gcode(ser, f"G0 Z-0.4")
                            time.sleep(0.2)
                # Simulate a tap on the enter key
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
                    # When 'esc' is pressed in this timeframe, exit the game.
                    send_gcode(ser, f"G0 X0 Y0")
                    time.sleep(10)
                    send_gcode(ser, f"G0 Z0")
                    time.sleep(0.5)
                    exit()
                
        # Wordle Game
        elif game_type_arg == "2":
            CHATGPTTOGGLE = False # Toggle to use the ChatGPT implementation or not.
            print("Wordle Game")
            wordle = Wordle()
            send_gcode(ser, f"G0 Z-0.4")
            time.sleep(0.2)
            # Move to the middle of the phone screen.
            x_middle = screen_tap_locations[6][1]
            y_middle = screen_tap_locations[6][2]
            send_gcode(ser, f"G0 X{x_middle} Y{y_middle}")
            time.sleep(10)

            # Simulate making guesses and getting feedback
            for attempt in range(wordle.max_attempts):
                if not CHATGPTTOGGLE:
                    # The most optimal guess is "crane", therefore we start with this.
                    if attempt == 0:
                        guess = "crane"
                    else:
                        # Make a guess using the Wordle make_guess function.
                        guess = wordle.make_guess()
                    if guess is None:
                        # If not more valid guesses, exit the game.
                        print("No valid guesses left!")
                        send_gcode(ser, f"G0 X0 Y0")
                        time.sleep(10)
                        send_gcode(ser, f"G0 Z0")
                        time.sleep(0.5)
                        break
                else:
                    # We utilize ChatGPT to make the guess.
                    guess = None
                    while guess is None:
                        # Keep generating a word, until a word in the right format is returned.
                        guess = wordle.make_guess_chatgpt()

                print(f"Guessing: {guess}")

                # Loop through the letters of the word and tap on the screen
                for letter in guess:
                    # Find the corresponding screen tap location
                    for loc in screen_tap_locations:
                        if loc[0] == letter:
                            # Simulate a tap on the screen at (x, y)
                            x, y = loc[1], loc[2]
                            print(f"Tapping on {letter} at ({x}, {y})")
                            send_gcode(ser, f"G0 X{x} Y{y}")
                            time.sleep(2)
                            send_gcode(ser, f"G0 Z-0.05")
                            time.sleep(0.5)
                            send_gcode(ser, f"G0 Z-0.4")
                            time.sleep(0.2)
                # Simulate a tap on the enter key
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
                # Extra correctness check
                # Sometimes, due the fast screen change from the Wordle to the congratulations screen,
                # the last guess is not correctly registered, causing the Wordle to not recognize
                # The game has finished. Therefore, an additional check is done to check if the game
                # has finished.
                is_correct = wordle.extra_correctness_check(guess)
                if is_correct:
                    print(f"Correct guess! The word was '{guess}'")
                    send_gcode(ser, f"G0 X0 Y0")
                    time.sleep(10)
                    send_gcode(ser, f"G0 Z0")
                    time.sleep(0.5)
                    break

                # Print the current attempt.
                print(f"Attempt {attempt + 1}/{wordle.max_attempts} failed.\n")


if __name__ == "__main__":
    main()