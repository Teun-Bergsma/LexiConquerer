from WordleHandler.Wordle import Wordle
import time
print("Wordle Game")

wordle = Wordle()


# Simulate making guesses and getting feedback
for attempt in range(wordle.max_attempts):
    guess = wordle.make_guess()
    if guess is None:
        print("No valid guesses left!")
        break
    input("Press 'Y' and Enter to continue: ").strip().upper() != 'Y' and exit("Exiting game.")
    print(f"Guessing: {guess}")
    is_correct = wordle.update_info(guess, attempt)
    if is_correct:
        print(f"Correct guess! The word was '{guess}'")
        break

    print(f"Attempt {attempt + 1}/{wordle.max_attempts} failed.\n")