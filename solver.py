import os
from ItsPrompt.prompt import Prompt as prompt
from colorama import Fore as fore, Style as style

class Solver():
    def __init__(self):
        self.systemRun = True
        self.wordList = []
        try:
            # Use a more robust relative path
            script_dir = os.path.dirname(__file__)
            file_path = os.path.join(script_dir, "words_ranked.txt")
            with open(file_path, "r") as wordFile:
                for line in wordFile:
                    word, frequency = line.strip().split(',')
                    self.wordList.append((word, int(frequency)))
            # Sort the word list by frequency in descending order
            self.wordList.sort(key=lambda x: x[1], reverse=True)
        except FileNotFoundError:
            print("Error: words_ranked.txt not found. Please ensure it's in the same directory as the script.")
            quit()
        except Exception as e:
            print(f"An error occurred while loading the word list: {e}")
            quit()

        self.current = ""
        self.format = ""
        self.no_list = []
        self.guessed_list = []

    def set_format(self):
        format_list = []
        for letter in self.current:
            if letter == "_":
                format_list.append(f"{fore.RED}{letter}{fore.RESET}")
            else:
                format_list.append(f"{fore.GREEN}{letter}{fore.RESET}")
        self.format = "".join(format_list)
        
    def set_pattern(self, pattern):
        self.current = pattern.lower()
        self.set_format()

    def set_incorrect_letters(self, letters):
        self.no_list = [l.strip().lower() for l in letters.split(';') if l.strip()]

    def run_analysis(self):
        """
        Analyzes each word in the pattern and prints individual results.
        """
        input_parts = self.current.split(' ')
        known_letters = set(self.no_list)
        for char in self.current.replace(' ', ''):
            if char != '_':
                known_letters.add(char.lower())
        
        print("\n--- Analysis ---")
        for part in input_parts:
            if '_' not in part:
                continue
            
            answerList = [word_freq for word_freq in self.wordList if self.check(word_freq[0], part)]
            
            print(f"\nFor word: '{part}'")

            
            if not answerList:
                print("No possible answers found.")
                continue

            print(f"Possible answers ({len(answerList)}): {[word for word, freq in answerList[:10]]}")

            prediction = self._predict_letter_for_answers(answerList, known_letters)
            if prediction:
                print(f"Predicted next letter: {prediction}")
            else:
                print("No new letters can be predicted for this word.")

    def _predict_letter_for_answers(self, answerList, known_letters):
        """
        Predicts the most likely next letter for a given list of answers.
        """
        letter_counts = {}
        if not answerList:
            return None

        for word, frequency in answerList:
            for letter in set(word.lower()):
                if letter not in known_letters:
                    letter_counts[letter] = letter_counts.get(letter, 0) + frequency

        if not letter_counts:
            return None

        return max(letter_counts, key=letter_counts.get)

    def check(self, word, pattern):
        if len(word) != len(pattern):
            return False

        letters_in_current = {char.lower() for char in self.current if char != '_'}
        
        # New check: Ensure no letters from no_list are in the word, except for those already in the pattern
        for char in word:
            if char in self.no_list and char not in letters_in_current:
                return False

        for i, char in enumerate(word):
            pattern_char = pattern[i].lower()
            word_char = char.lower()

            if pattern_char != '_' and pattern_char != word_char:
                return False
            
            if pattern_char == '_' and word_char in letters_in_current:
                return False

        return True

    def update_pattern(self, letter, positions):
        pattern_list = list(self.current)
        for pos in positions:
            if 0 <= pos < len(pattern_list):
                pattern_list[pos] = letter
            else:
                print(f"Warning: position {pos+1} is out of bounds.")
        self.current = "".join(pattern_list)
        self.set_format()

def play_game():
    solver = Solver()
    print("\033c", end="")
    print(f"Enter the word/phrase with '{fore.RED}_{fore.RESET}' replacing blanks")
    pattern = input(">")
    if not pattern: return
    solver.set_pattern(pattern)
    print("Enter any known incorrect letters (separated by ';')")
    incorrect_letters = input(">")
    solver.set_incorrect_letters(incorrect_letters)

    while '_' in solver.current:
        print("\033c", end="")
        print(f"Current pattern: {solver.format}")
        print(f"Incorrect letters: {fore.RED}{'; '.join(sorted(solver.no_list))}{fore.RESET}")
        
        solver.run_analysis()
        print("\nEnter a letter to guess (or press Enter to exit)")
        guess = input(">")
        if not guess:
            break
        
        guess = guess[0].lower()

        if guess in solver.no_list or guess in solver.current.lower():
            input(f"Letter '{guess}' has already been used. Press enter to continue.")
            continue

        was_correct = prompt.confirm(f"Was '{guess}' in the word?")

        if was_correct:
            while True:
                print(solver.format)
                x = False
                for i in range(len(solver.current)):
                    if x:
                        print(f"{fore.BLUE}{(i + 1) % 10}{fore.RESET}", end="")
                        x = False
                    else:
                        print(f"{fore.MAGENTA}{(i + 1) % 10}{fore.RESET}", end="")
                        x = True
                print(f"Enter the positions of '{guess}' in the word.")
                positions_str = input(f">")
                if not positions_str:
                    break
                try:
                    positions = [int(p.strip()) - 1 for p in positions_str.split(',')]
                    solver.update_pattern(guess, positions)
                    break 
                except ValueError:
                    print("Invalid input. Please enter comma-separated numbers.")
        else:
            solver.no_list.append(guess)
    
    print("\033c", end="")
    print(f"Final result: {solver.current}")
    if '_' not in solver.current:
        print("\nProgram terminated. Rerun?.")
    else:
        print("\nExited.")


if __name__ == "__main__":
    while True:
        if prompt.confirm("Run Hangman Solver?"):
            print("\033c", end="")
            play_game()
        else:
            quit()