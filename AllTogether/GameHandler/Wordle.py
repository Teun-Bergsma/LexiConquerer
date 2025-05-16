from PIL import Image #prob only works in venv
import random

from enum import Enum
from PhoneReader import phonereader

from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # Perform `export [API KEY]` in the terminal. A working API key can be found in the README.
)

class Wordle:
    def __init__(self):
        # Make self.word_list the contents of the fullNYTwordlelist.txt file
        try:
            with open('fullNYTwordlelist.txt', 'r') as f:
                self.word_list = [line.strip().lower() for line in f.readlines()]
        except FileNotFoundError:
            print("Word list file not found.")
            quit()
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

    def make_guess_chatgpt(self):
        # Generate a response by ChatGPT (GPT-4o-mini) with the input and user as input.
        # inputstr is the prompt for the model.
        inputstr = "You are a Wordle solver. I will give you the letters currently guessed, and note which letters are present in the final word and on the right position, the letters that are present in the final word but on the wrong position, and the letters that are not present in the final word. You will give me one English word consisting of 5 letters that respects these rules. Position 0 is the first letter, position 4 is the last letter."
 
        inputstr += "The letters that are present and in the correct position are:"
        # Ensure the word respects green letter positions
        if self.green_letters:
            for idx, letter in self.green_letters.items():
                inputstr += f" '{letter}' in position {idx},"
        else:
            inputstr += "No letters are present and in the correct position yet."
        # Ensure the word respects yellow letter positions
        inputstr += "The letters that ARE PRESENT but in the WRONG POSITION are:"
        if self.yellow_letters:
            for letter, bad_positions in self.yellow_letters.items():
                inputstr += f" '{letter}' SHOULD NOT BE IN position(s) {', '.join(map(str, bad_positions))},"
        else:
            inputstr += "No letters are present but in the wrong position yet."
        inputstr += "The letters that are NOT present in the word and thus you are NOT ALLOWED TO USE are:"
        
        # Ensure the word does not contain excluded letters
        if self.excluded_letters:
            for letter in self.excluded_letters:
                inputstr += f" '{letter}',"
        else:
            inputstr += "No letters are not present in the word yet."
        inputstr += "Please give me a word that respects these rules. Do not write any prior texts such as 'this word could work...'. I want ONLY what I described: ONE WORD."

        # Generate a response by ChatGPT (GPT-4o-mini) with the input and user as input.
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": inputstr,
                }
            ],
            model="gpt-4o-mini",
        )
        # Select only the direct textual response content of the total response.
        content = response.choices[0].message.content
        # Strip, lowercase and check if content is a valid 5 letter word.
        is_five_letters = content.strip().lower().isalpha() and len(content.strip().lower()) == 5
        if is_five_letters:
            # Return the word.
            return content.strip().lower()
        else:
            # If the response is not a valid 5 letter word, print an error message and return None.
            print("ChatGPT did not return a valid 5 letter word.")
            return None
    
    def is_valid_guess(self, word: str):
        # Ensure the word does not contain excluded letters
        if any(letter in self.excluded_letters for letter in word):
            return False
        
        # Ensure the word respects green letter positions
        for idx, letter in self.green_letters.items():
            if word[idx] != letter:
                return False
        
        # Ensure the word respects yellow letter positions
        for letter, bad_positions in self.yellow_letters.items():
            if letter not in word:
                return False
            if any(word[pos] == letter for pos in bad_positions):
                return False
        
        return True

    def update_info(self, guess: str, attempt:int):
        # Simulate the feedback you would get in Wordle
        # Get the screenshot of the game board

        wordle_reader = WordleReader()
        wordle_info = wordle_reader.get_board_info(screenshot=None)
        # Update the target word based on the feedback from the game
        this_word_info = wordle_info[attempt].info
        if this_word_info == (WordlePosition.CORRECT, WordlePosition.CORRECT, WordlePosition.CORRECT, WordlePosition.CORRECT, WordlePosition.CORRECT):
            return True
        print(guess)
        # for position, letter in enumerate(guess):
        #     if this_word_info[position] == WordlePosition.CORRECT:
        #         self.green_letters.update({position: letter})
        #     elif this_word_info[position] == WordlePosition.WRONGPLACE:
        #         if letter not in self.yellow_letters:
        #             self.yellow_letters[letter] = set()
        #         self.yellow_letters[letter].add(position)
        #     elif this_word_info[position] == WordlePosition.NOTPRESENT:
        #         print("Letter not present: ", letter, "with green letters: ", self.green_letters.values(), "and yellow letters: ", self.yellow_letters)
        #         if (letter not in self.green_letters.values() and letter not in self.yellow_letters):
        #             self.excluded_letters.add(letter)
        # First pass: collect green and yellow info
        for position, letter in enumerate(guess):
            if this_word_info[position] == WordlePosition.CORRECT:
                self.green_letters.update({position: letter})
            elif this_word_info[position] == WordlePosition.WRONGPLACE:
                if letter not in self.yellow_letters:
                    self.yellow_letters[letter] = set()
                self.yellow_letters[letter].add(position)

        # Second pass: mark exclusions only after green/yellow are known
        for position, letter in enumerate(guess):
            if this_word_info[position] == WordlePosition.NOTPRESENT:
                if (letter not in self.green_letters.values() and letter not in self.yellow_letters):
                    self.excluded_letters.add(letter)
        print("Green letters: ", self.green_letters)
        print("Yellow letters: ", self.yellow_letters)
        print("Excluded letters: ", self.excluded_letters)
        return False

class Word():
    def __init__(self, info:tuple):
        self.info = info

    def __repr__(self):
        return f"Word(info={self.info})"

class WordlePosition(Enum):
    CORRECT = 3
    WRONGPLACE = 2
    NOTPRESENT = 1

    def __str__(self):
        return self.name.lower()
    
class WordleReader:
    # Coords on the phone used
    x_coords: tuple = (85, 275, 465, 655, 845)
    y_coords: tuple = (400, 600, 800, 1000, 1200, 1400)
    # Coords on testing phone
    # x_coords: tuple = (50, 285, 525, 760, 1000)
    # y_coords: tuple = (500, 800, 1100, 1300, 1500, 1700)

    @staticmethod
    def get_pixel_info(img, x, y):
        r, g, b = img.getpixel((x, y))

        # if r == 120 and g == 124 and b == 126:
        #     return WordlePosition.NOTPRESENT
        if r == 181 and g == 159 and b == 59:
            return WordlePosition.WRONGPLACE
        elif r == 83 and g == 141 and b == 78:
            return WordlePosition.CORRECT
        else:
            print("Unknown color:", r, g, b)
            return WordlePosition.NOTPRESENT

    @classmethod
    def get_word_info(cls, img, word_int: int) -> Word:
        y = cls.y_coords[word_int]
        word_info = [None, None, None, None, None]

        for i in range(len(cls.x_coords)):
            x = cls.x_coords[i]
            word_info[i] = cls.get_pixel_info(img, x, y)

        return Word(tuple(word_info))

    @classmethod
    def get_board_info(cls, screenshot):
        phonereader.screenshot()
        img = Image.open("screen.png")
        img = img.convert("RGB")
        words = []
        for i in range(len(cls.y_coords)):
            word = cls.get_word_info(img, i)
            words.append(word)

        return tuple(words)