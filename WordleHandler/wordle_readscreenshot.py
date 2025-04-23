from PIL import Image
from enum import Enum

x_coords: tuple = (85, 275, 465, 655, 845)
y_coords: tuple = (400, 600, 800, 1000, 1200, 1400)

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

def get_pixel_info(img, x,y):
    r,g,b = img.getpixel((x,y))

    if r == 120 and g == 124 and b == 126:
        return WordlePosition.NOTPRESENT
    elif r == 201 and g == 180 and b == 88:
        return WordlePosition.WRONGPLACE
    elif r == 106 and g == 170 and b == 100:
        return WordlePosition.CORRECT
    else:
        print ("Unknown color:", r,g,b)
        return None

def get_word_info(img, word_int:int) -> Word:
    y = y_coords[word_int]
    word_info = [None,None,None,None,None]

    for i in range(len(x_coords)):
        x = x_coords[i]
        word_info[i] = get_pixel_info(img, x, y)

    return Word(tuple(word_info))

def get_board_info(screenshot) -> tuple[Word]:
    words = []
    for i in range(len(y_coords)):
        word = get_word_info(screenshot, i)
        words.append(word)

    return tuple(words)


img = Image.open("screen.png")
img = img.convert("RGB")
print(get_board_info(img))