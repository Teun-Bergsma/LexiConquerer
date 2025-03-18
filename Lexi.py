import pygame
import random
import sys

# Constants
WIDTH, HEIGHT = 500, 600
GRID_SIZE = 5
CELL_SIZE = 80
MARGIN = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 200, 0)
YELLOW = (200, 200, 0)

# Pick a random word from the fullNYTwordlelist.txt file
with open("fullNYTwordlelist.txt") as f:
    WORDS = f.read().splitlines()
WORD = random.choice(WORDS)
# Make the word uppercase
WORD = WORD.upper()
print(WORD)

# Load the list of valid words from allWords.txt
with open("allWords.txt") as f:
    validwords = f.read().splitlines()
valid_words = set(validwords)
# Make the words uppercase
valid_words = {word.upper() for word in valid_words}

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wordle in Pygame")
font = pygame.font.Font(None, 60)

# Game state
current_guess = ""
guesses = []

# Main loop
running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(current_guess) == GRID_SIZE and current_guess in valid_words:
                guesses.append(current_guess)
                current_guess = ""
                if guesses[-1] == WORD:
                    print("You guessed it!")
                    running = False
            elif event.key == pygame.K_BACKSPACE:
                current_guess = current_guess[:-1]
            elif event.unicode.isalpha() and len(current_guess) < GRID_SIZE:
                current_guess += event.unicode.upper()
    
    # Draw grid
    for i, guess in enumerate(guesses):
        for j, letter in enumerate(guess):
            rect = pygame.Rect(j * (CELL_SIZE + MARGIN) + 50, i * (CELL_SIZE + MARGIN) + 50, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            color = GRAY
            if letter == WORD[j]:
                color = GREEN
            elif letter in WORD:
                color = YELLOW
            pygame.draw.rect(screen, color, rect)
            text_surface = font.render(letter, True, BLACK)
            screen.blit(text_surface, rect.move(20, 20))
    
    # Draw current guess
    for j, letter in enumerate(current_guess):
        rect = pygame.Rect(j * (CELL_SIZE + MARGIN) + 50, len(guesses) * (CELL_SIZE + MARGIN) + 50, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, GRAY, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)
        text_surface = font.render(letter, True, BLACK)
        screen.blit(text_surface, rect.move(20, 20))
    
    pygame.display.flip()

pygame.quit()
sys.exit()
