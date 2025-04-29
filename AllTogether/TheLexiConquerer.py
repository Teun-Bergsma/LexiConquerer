import serial
import time
import random
import threading
import sys
import keyboard
# Important: make sure to install the scrcpy (https://github.com/Genymobile/scrcpy) on your system, otherwise this will not run.
# Phone needs to be connected to the computer and USB debugging enabled.
# from ppadb.client import Client as AdbClient
from PIL import Image
from enum import Enum
from typing import List

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

# Spelling Bee Game, Returns all the valid words that can be formed with the given letters
class SpellingBee:
    def __init__(self, valid_letters: List[str], required_letter: str):
        self.valid_letters = set(valid_letters)
        self.required_letter = required_letter.lower()
        self.words = self.load_dictionary()

    def load_dictionary(self) -> List[str]:
        # Load a dictionary file (you can use /usr/share/dict/words or a custom word list)
        try:
            with open('enable1WordList.txt', 'r') as f:
                words = [line.strip().lower() for line in f.readlines()]
        except FileNotFoundError:
            print("Dictionary file not found.")
            quit()
        return words

    def is_valid_word(self, word: str) -> bool:
        if len(word) < 4:
            return False
        if self.required_letter not in word:
            return False
        if not set(word).issubset(self.valid_letters):
            return False
        return True

    def find_valid_words(self) -> List[str]:
        return [word for word in self.words if self.is_valid_word(word)]   
    
class Wordle:
    def __init__(self, target_word: str):
        # Make self.word_list the contents of the fullNYTwordlelist.txt file
        try:
            with open('fullNYTwordlelist.txt', 'r') as f:
                self.word_list = [line.strip().lower() for line in f.readlines()]
        except FileNotFoundError:
            print("Word list file not found.")
            quit()
        self.target_word = target_word  # The correct word to guess
        self.guesses = []  # List to keep track of guesses
        self.max_attempts = 6  # Number of allowed guesses
        self.excluded_letters = set()  # Set of letters to exclude
        self.green_letters = {}  # Dictionary of green (correct) positions
        self.yellow_letters = {}  # Dictionary of yellow (incorrect positions but correct letters)
        
    def make_guess(self):
        # Filter out words based on excluded letters and green/yellow info
        valid_guesses = [word for word in self.word_list if self.is_valid_guess(word)]
        
        if not valid_guesses:
            print("No valid guesses left!")
            return None
        
        guess = random.choice(valid_guesses)
        self.guesses.append(guess)
        print(f"Making guess: {guess}")
        return guess
    
    def is_valid_guess(self, word: str):
        # Ensure the word does not contain excluded letters
        if any(letter in self.excluded_letters for letter in word):
            return False
        
        # Ensure the word respects green letter positions
        for idx, letter in self.green_letters.items():
            if word[idx] != letter:
                return False
        
        # Ensure the word respects yellow letter positions
        for letter, positions in self.yellow_letters.items():
            if letter not in word:
                return False
            if any(word[pos] == letter for pos in positions):
                return False
        
        return True

    def feedback(self, guess: str):
        # Simulate the feedback you would get in Wordle
        green = {}
        yellow = {}
        excluded = set()

        for i, (g, t) in enumerate(zip(guess, self.target_word)):
            if g == t:
                green[i] = g
            elif g in self.target_word:
                if g not in yellow:
                    yellow[g] = []
                yellow[g].append(i)
            else:
                excluded.add(g)
        
        # Update the green, yellow, and excluded letters
        self.green_letters.update(green)
        self.yellow_letters.update(yellow)
        self.excluded_letters.update(excluded)

        print(f"Green letters: {green}")
        print(f"Yellow letters: {yellow}")
        print(f"Excluded letters: {excluded}")
        
        # Return True if the guess was correct, False otherwise
        return guess == self.target_word

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
            ('a', 100, 200),
            ('b', 200, 200),
            ('c', 300, 200),
            ('d', 400, 200),
            ('e', 500, 200),
            ('f', 600, 200),
            ('g', 700, 200),
            ('h', 800, 200),
            ('i', 900, 200),
            ('j', 1000, 200),
            ('k', 1100, 200),
            ('l', 1200, 200),
            ('m', 1300, 200),
            ('n', 1400, 200),
            ('o', 1500, 200),
            ('p', 1600, 200),
            ('q', 1700, 200),
            ('r', 1800, 200),
            ('s', 1900, 200),
            ('t', 2000, 200),
            ('u', 2100, 200),
            ('v', 2200, 200),
            ('w', 2300, 200),
            ('x', 2400, 200),
            ('y', 2500, 200),
            ('z', 2600, 200),
            ('enter', 2700, 200),
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


            valid_letters = ['y', 'i', 't', 'f', 'd', 'g', 'e']
            required_letter = 'e'
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
            # print(f"Shuffled list: {shuffled_list}", type(shuffled_list))
            for word in shuffled_list:
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
                            send_gcode(ser, f"G0 Z-0.175")
                            time.sleep(0.2)
                            send_gcode(ser, f"G0 Z-0.4")
                            time.sleep(0.2)
                            # Simulate a tap on the screen at (x, y)
                print("Tapping on enter")
                x = screen_tap_locations[7][1]
                y = screen_tap_locations[7][2]
                send_gcode(ser, f"G0 X{x} Y{y}")
                time.sleep(2)
                send_gcode(ser, f"G0 Z-0.175")
                time.sleep(0.2)
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
            target_word = "dummy"  # Replace with the actual target word

            wordle = Wordle(target_word)
        
            # Simulate making guesses and getting feedback
            for attempt in range(wordle.max_attempts):
                guess = wordle.make_guess()
                if guess is None:
                    print("No valid guesses left!")
                    break
                is_correct = wordle.feedback(guess)
                if is_correct:
                    print(f"Correct guess! The word was '{guess}'")
                    break
                print(f"Attempt {attempt + 1}/{wordle.max_attempts} failed.\n")


if __name__ == "__main__":
    main()