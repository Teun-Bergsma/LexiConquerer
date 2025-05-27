from typing import List

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
        # Check if word is valid based on the given letters.
        if len(word) < 4:
            return False
        if self.required_letter not in word:
            return False
        if not set(word).issubset(self.valid_letters):
            return False
        return True

    def find_valid_words(self) -> List[str]:
        # Find all valid words that can be formed with the given letters.
        return [word for word in self.words if self.is_valid_word(word)]  