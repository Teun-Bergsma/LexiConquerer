from GameHandler.SpellingBee import SpellingBee
import serial
import time
import random
import threading
import sys

valid_letters = ['a', 'o', 'l', 'i', 'n', 't', 'y']
required_letter = 'y'
spelling_bee = SpellingBee(valid_letters, required_letter)
valid_words = spelling_bee.find_valid_words()
print(f"Found {len(valid_words)} valid words:")
shuffled_list = random.shuffle(valid_words)
shuffled_list = valid_words.copy()
random.shuffle(shuffled_list)
sorted_list = sorted(shuffled_list, key=len, reverse=True)
print(sorted_list)
exit()