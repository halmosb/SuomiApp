"""
Language learning app.

The original version is created for the Programming 1 course
at Tampere University
Course: COMP.CS.100 Programming 1
Project: Graphical User Interface - Advanced GUI
Name: Balazs Paszkal Halmos

This program implements a language practice app, which reads the wordlist
from a file and offers various methods to practice the vocablurary with
several options to adapt to different learning styles.

It is important that you always SAVE the changes in the settings,
    otherwise they will not have any effect. You can also cancel
    the changes that you made.

In the practice modes unless otherwise noted you can navigate with
    the keyboard, most often with the ENTER key.

Usage steps
 - Set the separator character
 - Open a word list file
 - Set extra settings if necessary
 - Save settings
 - Choose a practice mode
 - Start
 - Review the terms in the current batch
 - Start!
 - Practice
 - View statistics at the end of the rounds

The available settings on the settings tab:
Choose a file [file]: the file which contains the wordlist
Separator [string= ";"]: the character which separates the terms in the file
    this has to be set BEFORE opening the file
Shuffle [bool=True]: ask the terms in random order
Question language [string]: the language in which the questions are shown
Answer language [string]: the language in which you have to answer
Batch size [nonnegative int]: the word list can be split into smaller pieces
    e.g. only ask 8 words in one round
    if 0 all the words are asked in one round
Correct mistakes ["end", "round"]: if you make a mistake when
    should the program ask it again
Repeat until correct [bool=True]: if you make a mistake should it
    ask agin until you give a correct answer
Case sensitive answers [bool=False]: uppercase/lowercase matters
    in write mode
Trim punctuattion characters [string]: Those characters are
    ignored in the write mode, can be empty
Trim punctuation ["everywhere", "nowhere", "end"]: From where
    should it remove the punctuation marks

Notes on the settings:
    If there is an error a red error message shows what to do
    You have to save the settings before you start practicing
    It is allowed to choose the same language as question
        and answer e.g. to practice typing the words
    You can only start practicing after you saved the settings
        for the first time

If you started a learn mode you cannot change the settings
    until you finish the round

Learn modes:
 - List: only a list of the terms in the file
 - Flashcards: you can turn them with the SPACE
 - Write: written questions    

Example file content for the wordlist:
Finnish;English;Hungarian
omena.;apple;alma
jäätelö.;ice cream;fagyi
ananas.;pineapple;ananász
peruna.;potato;krumpli

[TODO] recordings, translate more files, timed practice, 
translate language in (), warning messiga when new file is opened
table when more columns, step back at the flashcards mode
Error: word! (something)
translate when tehre are emotyi lines in the file
correct the word while writing
"""
print("The program has started, it may take a few seconds.")
# Widgets
from tkinter import Tk, ttk, filedialog, StringVar, IntVar, Scrollbar, Text, Scale, Menubutton, Menu
# Constants
from tkinter import END, VERTICAL, HORIZONTAL, RAISED
SPEAK_AVAILABLE = True
TRANSLATE_AVAILABELE = True
try:
    # Reading the text
    import pygame
except:
    print("Speak is not available!")
    SPEAK_AVAILABLE = False
try:
    # Text to speech
    import gtts
    # Reading the text
except:
    print("Speak is not available!")
    SPEAK_AVAILABLE = False
# Translate
try:
    from deep_translator import GoogleTranslator
except:
    TRANSLATE_AVAILABELE = False
    print("Translate not available!")
# date
from datetime import datetime
import numpy as np
import pandas as pd
import time
import random
import re

FONT_SIZE = 14

# The different font settings (font family, size, weight)
FONTS = {
    "h1": ("Times", int(16/14*FONT_SIZE), "bold"),            # Header
    "p": ("Times", FONT_SIZE),                     # Paragraph
    "error": ("Times", FONT_SIZE),                 # Error label
    "help": ("Times", int(8/14*FONT_SIZE)),                   # Help label
    "table": ("Times", FONT_SIZE),                 # Table data
    "table_header": ("Times", FONT_SIZE, "bold"),  # Table header
    "write_entry": ("Times", FONT_SIZE)            # Write entry
}
# The used colors
COLORS = {
    "error": "#FF0000",             # Error label
    "help": "#8C8C8C",              # Help label
    "correct_answer": "#165E0C",    # Correct answer label
    "incorrect_answer": "#FF0000",  # Incorrect answer label
    "warning": "#c98612"
}
# The amount of necessary practice in hours
TARGET_PRACTICE = 1000

class GUI:
    """
    Language Learning App class.

    Implements all the functionality of the app. No input/return.
    """

    def __init__(self):
        # Text to speech
        pygame.mixer.init()
        self.__file_counter = 0
        # The main widget
        self.__main_window = Tk()
        # Title of the window
        self.__main_window.title("Language Learning App")
        # Size of the window
        self.__main_window.geometry(f"{int(600/14*FONT_SIZE)}x{int(870/14*FONT_SIZE)}")

        # The dictionary containing the word list data
        #     - key [string] the language
        #     - value [list of strings] the terms
        self.__word_list = {}
        # The settings dictionary
        #     the deafult values can be modified here
        self.__settings = {
            "wordlist_file": "",
            "separator": ";",
            "shuffle": True,
            "ques_langs": ["-"],
            "answ_lang": "-",
            "batch_size": 8,
            "correct_mistakes": "end",
            "case_sensitive_answers": False,
            "repeat_until_correct": True,
            "trim_punctuation_characters": [".", "!", "?"],
            "trim_punctuation": "end",
            "optional_answer_in_parentheses": True,
            "speak_enabled": True,
            "volume": 0.2,
            "statistics_file": "statistics.csv"
        }
        # The languages in the wordlist i.e. the header of the file as a list
        self.__languages = ["-"]
        # Number of terms to learn
        self.__number_of_words = -1
        # The index of the currently asked question
        self.__current_index = -1
        # The indecies in random order for the questions
        self.__question_indices = []
        # The indecies for the current round
        self.__current_question_indecies = []
        # The indecies of the mistakes that are made in the round
        self.__mistake_indecies = []
        # Counter of the correct answers
        self.__number_of_correct_answers = 0
        # Counter of the incorrect ansers
        self.__number_of_incorrect_answers = 0
        # Learn mode i.e "flashcards" or "write"
        self.__mode = ""
        # The tab on which the widgets are put
        self.__parent_tab = None
        # Keyboard control for the flashcards mode
        self.__flashcards_keyboard_active = False
        # Current practice time
        self.__practice_time = -1


        # The tab control panel
        self.__tabs = ttk.Notebook(self.__main_window)
        # The settings tab
        self.__settings_tab = ttk.Frame(self.__tabs)
        # The list tab
        self.__list_tab = ttk.Frame(self.__tabs)
        # The flashcards tab
        self.__flashcards_tab = ttk.Frame(self.__tabs)
        # The flashcards tab
        self.__write_tab = ttk.Frame(self.__tabs)
        # The translate tab
        self.__translate_tab = ttk.Frame(self.__tabs)

        # Adds the settins tab
        self.__tabs.add(self.__settings_tab, text = "Settings")
        # Adds the list tab, not avilable until the setting are saved
        self.__tabs.add(self.__list_tab, text = "List", state = "disabled")
        # Adds the flashcards tab not avilable until the setting are saved
        self.__tabs.add(self.__flashcards_tab, text = "Flashcards",
                        state = "disabled")
        # Adds the write tab not avilable until the setting are saved
        self.__tabs.add(self.__write_tab, text = "Write", state = "disabled")
        self.__tabs.add(self.__translate_tab, text = "Translate", state = "disabled")

        # Trigger for the tab change
        self.__tabs.bind("<<NotebookTabChanged>>", self.tab_changed)
        # Puts the tab control onto the main window
        self.__tabs.pack(expand= 1, fill= "both")
        # Trigger for the key pressed
        self.__main_window.bind("<KeyPress>", self.key_pressed)

        # ----- The Settings tab -----
        # -- File dialog --
        # Settings label
        ttk.Label(self.__settings_tab, text = "Settings",
                  font = FONTS["h1"]).grid(column = 0, row = 0,
                                         padx = 10, pady = 10)
        # Choose a file label
        ttk.Label(self.__settings_tab, text = "Choose a file:",
                  font = FONTS["p"]).grid(column = 0, row = 1)
        # File browser
        ttk.Button(self.__settings_tab, text = "Open",
                   command = self.open_file).grid(column = 1, row = 1)
        # Help label
        ttk.Label(self.__settings_tab,
                  text = "The file which contains the wordlist.",
                  font = FONTS["help"], foreground=COLORS["help"]).grid(column = 0,
                                row = 2, columnspan = 2, padx = 10)
        # -- Separator --
        # Separator label
        ttk.Label(self.__settings_tab, text = "Separator:",
                  font = FONTS["p"]).grid(column = 0, row = 3)
        # Help label
        ttk.Label(self.__settings_tab,
                text =f"The character which separates "
                "the terms in the wordlist file.",
                font = FONTS["help"], foreground=COLORS["help"]).grid(column = 0,
                    row = 4, columnspan = 2, padx = 10)
        # Separator entry
        self.__separator = ttk.Entry(self.__settings_tab)
        # Puts the separtor entry onto the window
        self.__separator.grid(column = 1, row = 3)
        # -- Shuffle --
        # Shuffle label
        ttk.Label(self.__settings_tab, text = "Shuffle:",
                  font = FONTS["p"]).grid(column = 0, row = 5)
        # Help label
        ttk.Label(self.__settings_tab,
                  text = "Ask the terms in random order.", font = FONTS["help"],
                  foreground=COLORS["help"]).grid(column = 0, row = 6,
                                                  columnspan = 2, padx = 10)
        # Shuffle var
        self.__shuffle_clicled = StringVar()
        # Setting the value
        self.__shuffle_clicled.set("True")
        # Dropdown
        self.__shuffle_btn = ttk.OptionMenu(self.__settings_tab,
                    self.__shuffle_clicled, "True", *["True", "False"])
        # Puts the dropdown onto the window
        self.__shuffle_btn.grid(column = 1, row = 5)
        # -- Question language --
        # Question label
        ttk.Label(self.__settings_tab, text = "Question language:",
                  font = FONTS["p"]).grid(column = 0, row = 7)
        # Help label
        ttk.Label(self.__settings_tab, text = "The language of the questions.",
                  font = FONTS["help"], foreground=COLORS["help"]).grid(column = 0,
                        row = 8, columnspan = 2, padx = 10)
        
        self.__question_mb = Menubutton (self.__settings_tab, text="Languages", relief=RAISED )
        self.__question_mb.grid(column = 1, row = 7)
        self.__question_mb.menu = Menu(self.__question_mb, tearoff = 0)
        self.__question_mb["menu"] = self.__question_mb.menu

        self.__ques_lang_clicled_items = [IntVar()]
        self.__question_mb.menu.add_checkbutton(label="-", variable=self.__ques_lang_clicled_items[0])
        """# Question variable
        self.__ques_lang_clicled = StringVar()
        # Setting the value
        self.__ques_lang_clicled.set("-")
        # Dropdown
        self.__ques_lang_btn = ttk.OptionMenu(self.__settings_tab,
                        self.__ques_lang_clicled, *self.__languages)
        # Puts the dropdown onto the window
        self.__ques_lang_btn.grid(column = 1, row = 7)"""
        
        
        # -- Answer language --
        # Answer label
        ttk.Label(self.__settings_tab, text = "Answer language:",
                  font = FONTS["p"]).grid(column = 0, row = 9)
        # Help label
        ttk.Label(self.__settings_tab, text = "The language of your answers.",
                  font = FONTS["help"], foreground=COLORS["help"]).grid(column = 0,
                        row = 10, columnspan = 2, padx = 10)
        # Answer variable
        self.__answ_lang_clicled = StringVar()
        # Set the value
        self.__answ_lang_clicled.set("-")
        # Dropdown
        self.__answ_lang_btn = ttk.OptionMenu(self.__settings_tab,
                        self.__answ_lang_clicled, *self.__languages)
        # Puts the dropdown onto the window
        self.__answ_lang_btn.grid(column = 1, row = 9)
        # -- Batch size --
        # Batch size label
        ttk.Label(self.__settings_tab, text = "Batch size:",
                  font = FONTS["p"]).grid(column = 0, row = 11)
        # Help label
        ttk.Label(self.__settings_tab,
                  text =f"The number of phrases asked in one round."
                  "(0 if all the words should be in one round).",
                  font = FONTS["help"], foreground=COLORS["help"]).grid(column = 0,
                        row = 12, columnspan = 2, padx = 10)
        # Batch size entry
        self.__batch_size = ttk.Entry(self.__settings_tab)
        # Puts the entrt onto the window
        self.__batch_size.grid(column = 1, row = 11)
        # -- Correct mistakes --
        # Correct mistakes label
        ttk.Label(self.__settings_tab, text = "Correct mistakes:",
                  font = FONTS["p"]).grid(column = 0, row = 13)
        # Help label
        ttk.Label(self.__settings_tab,
                  text =f"When to correct the mistakes: "
                    "[end] at the end of the round, "
                    "[round] in the round.", font = FONTS["help"],
                  foreground=COLORS["help"]).grid(column = 0, row = 14,
                                                  columnspan = 2, padx = 10)
        # Correct mistakes variable
        self.__correct_clicled = StringVar()
        # Setting the value
        self.__correct_clicled.set("-")
        # Dropdown
        self.__correct_btn = ttk.OptionMenu(self.__settings_tab,
                    self.__correct_clicled, "end", *["end", "round"])
        # Puts the dropdown onto the grid
        self.__correct_btn.grid(column = 1, row = 13)
        # -- Repeat until correct --
        # Repeat until correct label
        ttk.Label(self.__settings_tab, text = "Repeat until correct:",
                  font = FONTS["p"]).grid(column = 0, row = 15)
        # Help label
        ttk.Label(self.__settings_tab,
                  text =f"In write mode if you make a mistake it "
                  "will ask the word"
                  "until you give a correct answer.", font = FONTS["help"],
                  foreground=COLORS["help"]).grid(column = 0, row = 16,
                                                  columnspan = 2, padx = 10)
        # Repeat until correct variable
        self.__repeat_until_correct_clicled = StringVar()
        # Setting the value
        self.__repeat_until_correct_clicled.set("True")
        # Dropdown
        self.__repeat_until_correct_btn = ttk.OptionMenu(self.__settings_tab,
                self.__repeat_until_correct_clicled,
                    "True", *["True", "False"])
        # Puts the dropdown onto the window
        self.__repeat_until_correct_btn.grid(column = 1, row = 15)
        # -- Case sensiteive answers --
        # Case sensiteive answers label
        ttk.Label(self.__settings_tab, text = "Case sensiteive answers:",
                  font = FONTS["p"]).grid(column = 0, row = 17)
        # Help label
        ttk.Label(self.__settings_tab,
                  text = "In write mode the UPPERCASE/lowercase matters.",
                  font = FONTS["help"], foreground=COLORS["help"]).grid(column = 0,
                        row = 18, columnspan = 2, padx = 10)
        # Case sensiteive answers variable
        self.__case_sensitive_answers_clicled = StringVar()
        # Setting the value
        self.__case_sensitive_answers_clicled.set("True")
        # Dropdown
        self.__case_sensitive_answers_btn = ttk.OptionMenu(self.__settings_tab,
                        self.__case_sensitive_answers_clicled,
                            "True", *["True", "False"])
        # Puts the dropdown onto the window
        self.__case_sensitive_answers_btn.grid(column = 1, row = 17)
        # -- Trim punctuation characters --
        # Trim punctuation characters label
        ttk.Label(self.__settings_tab, text = "Trim punctuation characters:",
                  font = FONTS["p"]).grid(column = 0, row = 19)
        # Help label
        ttk.Label(self.__settings_tab,
                  text = "The characters which are ignored in write mode.",
                  font = FONTS["help"],
                  foreground=COLORS["help"]).grid(column = 0, row = 20,
                                                  columnspan = 2, padx = 10)
        # Trim punctuation characters entry
        self.__trim_characters = ttk.Entry(self.__settings_tab)
        # Puts the entry onto the window
        self.__trim_characters.grid(column = 1, row = 19)
        # -- Trim punctuation --
        # Trim punctuation label
        ttk.Label(self.__settings_tab, text = "Trim punctuation:",
                  font = FONTS["p"]).grid(column = 0, row = 21)
        # Help label
        ttk.Label(self.__settings_tab,
                  text = "From where does it ignore punctuation in write mode.",
                  font = FONTS["help"], foreground=COLORS["help"]).grid(column = 0,
                            row = 22, columnspan = 2, padx = 10)
        # Trim punctuation variable
        self.__trim_position_clicled = StringVar()
        # Sets the value
        self.__trim_position_clicled.set("everywhere")
        # Dropdown
        self.__trim_position_btn = ttk.OptionMenu(
            self.__settings_tab, self.__trim_position_clicled, "everywhere",
            *["everywhere", "nowhere", "end"])
        # Puts the dropdown onto the window
        self.__trim_position_btn.grid(column = 1, row = 21)
        
        # -- Optional answers in parentheses --
        # Shuffle label
        ttk.Label(self.__settings_tab, text = "Optional answers in parentheses:",
                  font = FONTS["p"]).grid(column = 0, row = 23)
        # Help label
        ttk.Label(self.__settings_tab,
                  text = "If a part of a term is in parentheses do you have to enter it?", font = FONTS["help"],
                  foreground=COLORS["help"]).grid(column = 0, row = 24,
                                                  columnspan = 2, padx = 10)
        # Shuffle var
        self.__optional_answers_clicled = StringVar()
        # Setting the value
        self.__optional_answers_clicled.set("True")
        # Dropdown
        self.__optional_answers_btn = ttk.OptionMenu(self.__settings_tab,
                    self.__optional_answers_clicled, "True", *["True", "False"])
        # Puts the dropdown onto the window
        self.__optional_answers_btn.grid(column = 1, row = 23)

        # -- speak enabled --
        # Shuffle label
        ttk.Label(self.__settings_tab, text = "Speak enabled:",
                  font = FONTS["p"]).grid(column = 0, row = 25)
        # Help label
        ttk.Label(self.__settings_tab,
                  text = "Should it read the terms?", font = FONTS["help"],
                  foreground=COLORS["help"]).grid(column = 0, row = 26,
                                                  columnspan = 2, padx = 10)
        # Shuffle var
        self.__speak_enabled_clicled = StringVar()
        if SPEAK_AVAILABLE:
            # Setting the value
            self.__speak_enabled_clicled.set("True")
            # Dropdown
            self.__speak_enabled_btn = ttk.OptionMenu(self.__settings_tab,
                    self.__speak_enabled_clicled, "True", *["True", "False"])
        else:
            # Setting the value
            self.__speak_enabled_clicled.set("False")
            # Dropdown
            self.__speak_enabled_btn = ttk.OptionMenu(self.__settings_tab,
                    self.__speak_enabled_clicled, "False", *["True"])
        # Puts the dropdown onto the window
        self.__speak_enabled_btn.grid(column = 1, row = 25)

        # -- Volume --
        # volume label
        ttk.Label(self.__settings_tab, text = "Volume:",
                  font = FONTS["p"]).grid(column = 0, row = 27)
        self.__volume = Scale(self.__settings_tab, from_=0, to=100, orient=HORIZONTAL)
        self.__volume.set(20)
        self.__volume.grid(column = 1, row = 27)

        # -- Test volume --
        ttk.Label(self.__settings_tab, text = "Test volume:",
                  font = FONTS["p"]).grid(column = 0, row = 29)
        # Test volume
        ttk.Button(self.__settings_tab, text = "Test",
                   command = self.test_volume).grid(column = 1, row = 29,
                                                    pady = 10)

        # -- Statistics File dialog --
        # Choose a file label
        ttk.Label(self.__settings_tab, text = "Choose a statistics file:",
                  font = FONTS["p"]).grid(column = 0, row = 30)
        # File browser
        ttk.Button(self.__settings_tab, text = "Open",
                   command = self.open_statistics_file).grid(column = 1, row = 30)
        # Help label
        ttk.Label(self.__settings_tab,
                  text = "The file which contains the statistics.",
                  font = FONTS["help"], foreground=COLORS["help"]).grid(column = 0,
                                row = 31, columnspan = 2, padx = 10)
        try:
            open(self.__settings["statistics_file"])
        except:
            self.__settings["statistics_file"] = "-"
        self.__statistics_file_label = ttk.Label(self.__settings_tab,
                  text = f"Current file: {self.__settings['statistics_file']}",
                  font = FONTS["help"])
        self.__statistics_file_label.grid(column = 0,
                                row = 32, columnspan = 2, padx = 10)
        # -- Error label --
        self.__error_label = ttk.Label(
            self.__settings_tab, text = "", foreground=COLORS["error"])
        # Puts the label onto the window
        self.__error_label.grid(column = 0, row = 40, columnspan = 4)
        # -- Info label --
        self.__info_label = ttk.Label(self.__settings_tab, text = " ")
         # Puts the label onto the window
        self.__info_label.grid(column = 0, row = 41, columnspan = 4)
        # -- Warning label --
        self.__warning_label = ttk.Label(self.__settings_tab, text = " ", foreground=COLORS["warning"])
         # Puts the label onto the window
        self.__warning_label.grid(column = 0, row = 42, columnspan = 4)

        # -- Buttons --
        # Save button
        ttk.Button(self.__settings_tab, text = "Save",
                   command = self.save_settings).grid(column = 0, row = 43)
        # Cancel button
        ttk.Button(self.__settings_tab, text = "Cancel",
                   command = self.cancel_settings).grid(column = 1,
                                                      row = 43)
        # Quit button
        ttk.Button(self.__settings_tab, text = "Do NOT press this",
                   command = self.quit).grid(column = 0, row = 44, pady=10)

        # ----- Learning tabs -----
        # The List tab
        # List tab label
        ttk.Label(self.__list_tab, text = "List of phrases",
                  font = FONTS["h1"]).grid(column = 0, row = 0, padx = 10, pady = 10)

        # Translate tab
        ttk.Label(self.__translate_tab, text = "Translate",
                  font = FONTS["h1"]).grid(column = 0, row = 0, padx = 10, pady = 10, columnspan=2)

        # Answer label
        ttk.Label(self.__translate_tab, text = "Source language:",
                  font = FONTS["p"]).grid(column = 0, row = 1)
        # Help label
        ttk.Label(self.__translate_tab, text = "From which language should it translate?",
                  font = FONTS["help"], foreground=COLORS["help"]).grid(column = 0,
                        row = 2, columnspan = 2, padx = 2)
        # Answer variable
        self.__translate_clicled = StringVar()
        # Set the value
        self.__translate_clicled.set("-")
        # Dropdown
        self.__translate_btn = ttk.OptionMenu(self.__translate_tab,
                        self.__translate_clicled, *self.__languages)
        # Puts the dropdown onto the window
        self.__translate_btn.grid(column = 1, row = 1)

        # Target language
        ttk.Label(self.__translate_tab, text = "Target language:",
                  font = FONTS["p"]).grid(column = 0, row = 3)
        # Help label
        ttk.Label(self.__translate_tab, text = "To which language should it translate?",
                  font = FONTS["help"], foreground=COLORS["help"]).grid(column = 0,
                        row = 4, columnspan = 2, padx = 2)
        self.__translate_target = StringVar()
        self.__translate_target_entry = ttk.Entry(self.__translate_tab, textvariable=self.__translate_target)
        self.__translate_target_entry.grid(column = 1, row = 3)
        self.__translate_button = ttk.Button(self.__translate_tab, text = "Translate", command=self.translate)
        self.__translate_button.grid(column=0, row=5, columnspan=2, pady=10)
        self.__save_translation_button = ttk.Button(self.__translate_tab, text = "Save to file", command=self.save_translation)
        self.__save_translation_button.grid(column=0, row=6, columnspan=2, pady=10)
        # Error label
        self.__translate_error_label = ttk.Label(self.__translate_tab, text = " ", foreground=COLORS["error"], wraplength=500)
         # Puts the label onto the window
        self.__translate_error_label.grid(column = 0, row = 7, columnspan = 4)
        # Flashcards tab
        # Flashcards label
        ttk.Label(self.__flashcards_tab, text = "Flashcards Mode",
                  font = FONTS["h1"]).grid(
            column  = 0, row = 0, columnspan = 2, padx = 10, pady = 10)
        # Start button
        self.__flashcards_start_button = ttk.Button(
            self.__flashcards_tab, text = "Start",
                command = self.flashcards_mode_start)
        # Puts the button onto the window
        self.__flashcards_start_button.grid(column = 0, row = 1)
        # Flashcard
        self.__flashcard_button = ttk.Button(
            self.__flashcards_tab, text = "...",
                command = self.flashcard_button)
        # Start button 2
        self.__flashcards_start_button2 = ttk.Button(
            self.__flashcards_tab, text = "Start!",
                command = self.flashcards_mode_flashcards)
        # Correct button
        self.__flashcards_correct_button = ttk.Button(
            self.__flashcards_tab, text = "Correct",
                command = self.correct_answer)
        # Incorrect button
        self.__flashcards_incorrect_button = ttk.Button(
            self.__flashcards_tab, text = "Inorrect",
                command = self.incorrect_answer)
        # Sets the columnwidth
        self.__flashcards_tab.columnconfigure(0, weight= 1)

        # Write tab
        # Write label
        ttk.Label(self.__write_tab, text = "Write Mode",
                  font = FONTS["h1"]).grid(
            column = 0, row = 0, columnspan = 2, padx = 10, pady = 10)
        # Start button
        self.__write_start_button = ttk.Button(
            self.__write_tab, text = "Start", command = self.write_mode_start)
        # Puts the button onto the window
        self.__write_start_button.grid(column = 0, row = 1)
        # Start button 2
        self.__write_start_button2 = ttk.Button(
            self.__write_tab, text = "Start!", command = self.write_mode_write)
        # Sets the width of the column
        self.__write_tab.columnconfigure(0, weight= 1)
        # Question label
        self.__write_question_label = ttk.Label(self.__write_tab)
        # Check button
        self.__write_check_button = ttk.Button(self.__write_tab, text = "Check")
        # Answer entry
        self.__write_answer_entry = Text(self.__write_tab, height= 5, width = 50)
        # Answer entry scrollbar
        self.__write_answer_entry_scrollbar = Scrollbar(self.__write_tab)
        # Correct answer label
        self.__write_correct_answer_label = ttk.Label(self.__write_tab)
        # Next button
        self.__write_next_button = ttk.Button(self.__write_tab, text = "Next")

        # Common to learn modes
        self.__congrat_label = ttk.Label()

        # Setup
        # Sets the default settings
        self.cancel_settings()
        # Adds the error message
        self.set_message("error", "You haven't chosen a wordlist file!")
        # Starts the GUI
        self.__main_window.mainloop()

    def translate(self):
        self.set_message()
        source_lang = self.__translate_clicled.get()
        target_lang = self.__translate_target_entry.get()
        target_lang = self.clean_word(target_lang)
        if target_lang == "":
            self.set_message("translate_error", "The target language has to be given!")
            return
        try:
            translated = GoogleTranslator(source=source_lang.lower(), target=target_lang.lower()).translate_batch(self.__word_list[source_lang])
            self.__word_list[target_lang] = translated
            self.__languages = list(self.__word_list.keys())
            # Prints the word list
            self.print_word_list(self.__languages, range(
                self.__number_of_words), self.__translate_tab, 20, None, 2)
            self.__translate_tab.columnconfigure(0, weight=1)
            self.__translate_tab.columnconfigure(1, weight=1)
        except Exception as e:
            self.set_message("translate_error", f"{e}")
            return

    def save_translation(self):
        word_list = pd.DataFrame(self.__word_list)
        word_list.to_csv(self.__settings["wordlist_file"], sep=self.__settings["separator"], index=False)
        self.setings_after_new_word_list()


    def test_volume(self):
        self.read_text("Is the volume correct?", "en")

    def tab_changed(self, event):
        """
        When the active tab is changed changes the binds and
            the focus of the corresponding start buttons.
        
        :param event: event, the click event.
        """
        # Gets the currnetly active tab index
        current_tab = self.__tabs.index(self.__tabs.select())
        # Flashcards tab
        if current_tab == 2:
            # Unbinds the start button of the write mode
            self.unbind_event('<Return>', self.write_mode_start)
            # Binds the start button of the flashcards mode
            self.__main_window.bind('<Return>', self.flashcards_mode_start)
            # Sets the focus
            self.__flashcards_start_button.focus()
        # Write tab
        elif current_tab == 3:
            # Unbinds the start button of the flashcards mode
            self.unbind_event('<Return>', self.flashcards_mode_start)
            # Binds the start button of the write mode
            self.__main_window.bind('<Return>', self.write_mode_start)
            # Sets the focus
            self.__write_start_button.focus()
        # List or settings tab
        else:
            # Unbinds the start button of the write mode
            self.unbind_event('<Return>', self.write_mode_start)
            # Unbinds the start button of the flashcards mode
            self.unbind_event('<Return>', self.flashcards_mode_start)

    def write_mode_start(self, event = None):
        """
        Starts the write mode.

        :param event: event, the click event, necessary.
        """
        # Sets the mode
        self.__mode = "write"
        # Sets the parent tab
        self.__parent_tab = self.__write_tab
        # Starts the timer
        self.start_timer()

    def flashcards_mode_start(self, event = None):
        """
        Starts the write mode.

        :param event: event, the click event, necessary.
        """
        # Sets the mode
        self.__mode = "flashcards"
        # Sets the parent tab
        self.__parent_tab = self.__flashcards_tab
        # Starts the timer
        self.start_timer()

    def start_timer(self, event = None):
        """
        Starts the timer.

        :param event: event, the click event, necessary.
        """
        # Sets the current time
        self.__practice_time = time.time()
        # Starts the learn mode i.e write or flashcards
        self.learn_mode()

    def learn_mode(self, event = None):
        """
        Before the starting of the lear mode this function
            sets the active tabs. And manages the asked
            batches.
        
        :param event: event, the click event, necessary.
        """
        # Settings tab disabled
        self.__tabs.tab(0, state = "disabled")
        self.__tabs.tab(4, state = "disabled")
        # List tab disabled
        self.__tabs.tab(1, state="disabled")
        if self.__mode == "write":
            # Flashcards tab disabled
            self.__tabs.tab(2, state = "disabled")
        elif self.__mode == "flashcards":
            # Write tab disabled
            self.__tabs.tab(3, state = "disabled")
        # Clears the unnecessary buttons
        self.clear_buttons()
        # If random order
        if self.__settings["shuffle"]:
            # Mixes the questions
            random.shuffle(self.__question_indices)
        # If there were no mistakes
        if len(self.__mistake_indecies) == 0:
            # If the batch size is 0, i.e. everything is in one batch
            if self.__settings["batch_size"] == 0:
                # All of the words are currently asked
                self.__current_question_indecies = list(self.__question_indices)
                # Shows the recap list
                self.learn_mode_list()
            # If there are batches
            else:
                # Checks for the last elements
                try:
                    # Sets the currently asked indecies
                    self.__current_question_indecies = list(
                        self.__question_indices[0:self.__settings["batch_size"]])
                    # Removes the currently asked indecies
                    self.__question_indices[0:self.__settings["batch_size"]] = []
                # If we are in the last few elemnts
                except:
                    # All of the last elements are asked
                    self.__current_question_indecies = list(
                        self.__question_indices[0:])
                    # Clears the list
                    self.__question_indices = []
                # If all the questions are answered
                if len(self.__current_question_indecies) == 0 and len(self.__question_indices) == 0:
                    # End
                    self.learn_mode_end()
                else:
                    # Next round
                    self.learn_mode_list()
        # If there were mistakes in the previous round
        else:
            # The mistakes are asked agin
            self.__current_question_indecies = list(self.__mistake_indecies)
            # The mistakes list id vleared
            self.__mistake_indecies = []
            # Next round
            self.learn_mode_list()

    def learn_mode_list(self):
        """
        Shows the recap list in the beginning of the round
            of the terms which will be asked in this round.
            No parameter.
        """
        # Flashcards mode
        if self.__mode == "flashcards":
            # The start button 2
            self.__flashcards_start_button2 = ttk.Button(
                self.__parent_tab, text = "Start!", command = self.flashcards_mode_flashcards)
            # Puts the button onto the window
            self.__flashcards_start_button2.grid(column = 0, row = 1)
            # Sets the focus
            self.__flashcards_start_button2.focus()
            # Binds the return key to the button
            self.__main_window.bind(
                '<Return>', self.flashcards_mode_flashcards)
        # Write mode
        elif self.__mode == "write":
            # The start button 2
            self.__write_start_button2 = ttk.Button(
                self.__parent_tab, text = "Start!", command = self.write_mode_write)
            # Puts the button onto the window
            self.__write_start_button2.grid(column = 0, row = 1)
            # Sets the focus
            self.__write_start_button2.focus()
            # Binds the return key to the button
            self.__main_window.bind('<Return>', self.write_mode_write)
        # Gets the list
        self.__list = self.print_word_list(
            [*self.__settings["ques_langs"], self.__settings["answ_lang"]],
                self.__current_question_indecies, self.__parent_tab)
        """self.__list = self.print_word_list(
            [self.__settings["ques_lang"], self.__settings["answ_lang"]],
                self.__current_question_indecies, self.__parent_tab)"""
        # Shiffels the questions
        if self.__settings["shuffle"]:
            random.shuffle(self.__current_question_indecies)
        # Sets the columnwidths
        self.__parent_tab.columnconfigure(1, weight= 0)
        self.__parent_tab.columnconfigure(0, weight= 1)

    def key_pressed(self, event):
        """
        Key pressed event. Used in flashcards mode
            to flip or discard the card.
        
        :param event: event, the click event, necessary.
        """
        # The pressed key
        key = event.keysym.lower()
        # If flashcards mode is active
        if self.__flashcards_keyboard_active and key == "i":
            # Incorrect answer
            self.incorrect_answer()
        elif self.__flashcards_keyboard_active and key == "c":
            # Correct answer
            self.correct_answer()
        elif self.__flashcards_keyboard_active and key == "space":
            # Flips the card
            self.flashcard_button()

    def flashcards_mode_flashcards(self, event = None):
        """
        Shows the flashcards.

        :param event: event, the click event, necessary.
        """
        # Clears the unncessary widgets
        self.clear_list()
        # Activates the flashcards mode
        self.__flashcards_keyboard_active = True
        # Shows the question first
        #self.__flashcard_shown_language = self.__settings["ques_lang"]
        self.__flashcard_show_question = True
        # The flashcard
        self.__flashcard_button = ttk.Button(
            self.__parent_tab, text = "...", command = self.flashcard_button)
        # Puts the flashcard onto the window
        self.__flashcard_button.grid(column = 0, row = 2,
                                     columnspan = 2, pady = 40)
        # Correct button
        self.__flashcards_correct_button = ttk.Button(
            self.__parent_tab, text = "[C] Correct",
            command = self.correct_answer)
        # Puts the button onto the window
        self.__flashcards_correct_button.grid(column = 0, row = 3, pady = 20)
        # Incorrect button
        self.__flashcards_incorrect_button = ttk.Button(
            self.__parent_tab, text = "[I] Incorrect",
            command = self.incorrect_answer)
        # Puts the button onto the window
        self.__flashcards_incorrect_button.grid(column = 1, row = 3, pady = 20)
        # Sets the width of the column
        self.__parent_tab.columnconfigure(1, weight= 1)

        # Are there any remaining question
        if len(self.__current_question_indecies) > 0:
            # The current index is the 0th
            self.__current_index = self.__current_question_indecies[0]
            # Sets the button text
            if self.__flashcard_show_question:
                text = (self.__settings["separator"]+"\n").join([
                    self.__word_list[x][self.__current_index] for x in self.__settings["ques_langs"]
                ])
            else:
                text = self.__word_list[self.__settings["answ_lang"]][self.__current_index]
            self.__flashcard_button.configure(text = text)
        else:
            # If there are no more questions
            if len(self.__mistake_indecies) == 0 and self.__settings["batch_size"] == 0:
                # If there were no mistakes - End
                self.learn_mode_end()
            else:
                # Clears the unncessary widgets
                self.clear_buttons()
                # Next round
                self.learn_mode()



    def write_mode_write(self, event = None):
        """
        Shows the questions in qrite mode.

        :param event: event, the click event, necessary.
        """

        # Clears the unncessary widgets
        self.clear_list()
        # Binds return to checking the answer
        self.__main_window.bind('<Return>', self.write_check_anwer)
        # Question label
        self.__write_question_label = ttk.Label(
            self.__write_tab, text = "...", wraplength= 415, font = FONTS["p"])
        # Puts the label onto the window
        self.__write_question_label.grid(column = 0, row = 1)
        # Answer entry
        self.__write_answer_entry = Text(
            self.__write_tab, height= 5, width = 50, font = FONTS["write_entry"])
        # Puts the entry onto the window
        self.__write_answer_entry.grid(column = 0, row = 2)
        # Sets the focus
        self.__write_answer_entry.focus()
        # Sets the entry to enabled
        self.__write_answer_entry.config(state = "normal")
        # The scrollbar for the textbox
        self.__write_answer_entry_scrollbar = Scrollbar(self.__write_tab)
        # Sets the scrollbar
        self.__write_answer_entry.configure(
            yscrollcommand = self.__write_answer_entry_scrollbar.set)
        self.__write_answer_entry_scrollbar.configure(
            command = self.__write_answer_entry.yview)
        # Puts the scrollbar onto the window
        self.__write_answer_entry_scrollbar.grid(column = 1, row = 2, sticky = "nse")
        # Check button
        self.__write_check_button = ttk.Button(
            self.__write_tab, text = "Check", command = self.write_check_anwer)
        # Puts the button onto the window
        self.__write_check_button.grid(column = 0, row = 3)

        # Are there any remaining questions
        if len(self.__current_question_indecies) > 0:
            # The next question index
            self.__current_index = self.__current_question_indecies[0]
            # The question
            """self.__question = self.__word_list[self.__settings["ques_lang"]
                                               ][self.__current_index]"""
            self.__question = (self.__settings["separator"]+"\n").join([
                self.__word_list[x][self.__current_index] for x in self.__settings["ques_langs"]
            ])
            # The correct answer
            self.__correct_answer = self.__word_list[self.__settings["answ_lang"]
                                                     ][self.__current_index]
            # Set the question label
            self.__write_question_label.configure(
                text =f'What does\n{self.__question}\nmean in {self.__settings["answ_lang"]}?')

        else:
            # No more questions
            if len(self.__mistake_indecies) == 0 and self.__settings["batch_size"] == 0:
                # NO mistakes - End
                self.learn_mode_end()
            else:
                # Clears the unncessary widgets
                self.clear_buttons()
                # Next round
                self.learn_mode()

    def read_text(self, text, language="en"):
        if self.__settings["speak_enabled"]:
            if language not in gtts.lang.tts_langs():
                for lang in gtts.lang.tts_langs():
                    if gtts.lang.tts_langs()[lang].lower() == self.clean_word(self.remove_nested_parentheses(self.__settings["answ_lang"]).lower()):
                        language = lang
            tts = gtts.gTTS(text=text, lang=language)
            self.__file_counter += 1
            self.__file_counter %= 2
            tts.save(f'hello-{self.__file_counter}.mp3')
            pygame.mixer.music.load(f'hello-{self.__file_counter}.mp3')
            pygame.mixer.music.set_volume(self.__settings["volume"])
            pygame.mixer.music.play(loops=1)

    def write_check_anwer(self, event = None):
        """
        Checks if your answer is correct.

        :param event: event, the click event, necessary.
        """
        self.read_text(self.__correct_answer, self.__settings["answ_lang"])
        # Unbinds return from the button
        self.unbind_event('<Return>', self.write_check_anwer)
        # Deletes check button
        self.delete_widget(self.__write_check_button)
        # Correct answer label
        self.__write_correct_answer_label = ttk.Label(
            self.__write_tab, text = "...", wraplength = 415, font = FONTS["p"])
        # Puts the label onto the window
        self.__write_correct_answer_label.grid(column = 0, row = 3)
        # Next button
        self.__write_next_button = ttk.Button(self.__write_tab, text = "Next")
        # Puts the button onto the grid
        self.__write_next_button.grid(column = 0, row = 4)
        # Deletes the \n from the end of the text entry
        if self.__write_answer_entry.get("end-1c", END) == "\n":
            self.__write_answer_entry.delete("end-1c", END)
        given_answer = self.__write_answer_entry.get("0.0", END).strip().replace("\n","")
        # Is answer correct
        if self.words_match(given_answer, self.__correct_answer):
            # Correct label
            self.__write_correct_answer_label.configure(
                text =f'Correct, the answer is "{self.__correct_answer}".',
                foreground=COLORS["correct_answer"])
            # Next word
            self.__write_next_button.configure(command = self.correct_answer)
            # Binds the return to the button
            self.__main_window.bind('<Return>', self.correct_answer)
        else:
            # Incorrect answer
            # Incorrect answer label
            self.__write_correct_answer_label.configure(
                text =f'Wrong, the answer is "{self.__correct_answer}".',
                foreground=COLORS["incorrect_answer"])
            for i in range(max(len(given_answer), len(self.__correct_answer))):
                try:
                    if self.__write_answer_entry.get(f"1.{i}", f"1.{i+1}") != self.__correct_answer[i]:
                        self.__write_answer_entry.tag_add("INCORRECT", f"1.{i}", f"1.{i+1}")
                except:
                    self.__write_answer_entry.tag_add("INCORRECT", f"1.{i}", f"1.{i+1}")

            self.__write_answer_entry.tag_configure("INCORRECT", foreground=COLORS["incorrect_answer"])
            # If repeat until correct
            if self.__settings["repeat_until_correct"]:
                # Sets the next button command
                self.__write_next_button.configure(
                    command = self.write_check_answer_button)
                # Binds the return to the button
                self.__main_window.bind(
                    '<Return>', self.write_check_answer_button)
                # Disables the entry
                self.__write_answer_entry.config(state = "disabled")
            else:
                # Sets the next button command to next word
                self.__write_next_button.configure(
                    command = self.incorrect_answer)
                # Binds the return to the button
                self.__main_window.bind('<Return>', self.incorrect_answer)

    def write_check_answer_button(self, event = None):
        """
        Checks the answer until it is correct.

        :param event: event, the click event, necessary.
        """
        # Enables the text entry
        self.__write_answer_entry.config(state = "normal")
        # Correct answer
        if self.words_match(self.__write_answer_entry.get("0.0", END).strip().replace("\n",""), self.__correct_answer):
            # It will ask it again later
            self.incorrect_answer()
        else:
            # Sets label
            self.__write_correct_answer_label.configure(text = f"Try again! ({self.__correct_answer})")
            # Clears entry
            self.__write_answer_entry.delete("0.0", END)

    def words_match(self, answ, ques):
        """
        Does the answer matches the question.

        :param answ: string, your answer
        :param ques: string, the correct answer
        :return bool, is the answer correct
        """
        # Cleans the word
        answ = self.clean_word(answ)
        # A list of the possibly acceptable answers
        acceptable_answers = [ques]
        # IF trim punctuations
        if self.__settings["trim_punctuation"] == "everywhere":
            # Translation table
            translation_table = str.maketrans('', '', ''.join(
                self.__settings["trim_punctuation_characters"]))
            # Adds the another poissible answer
            acceptable_answers.append(ques.translate(translation_table))
        elif self.__settings["trim_punctuation"] == "end":
            # The word
            trimmed_word = ques
            # Until all the unnecesary characers are removed from the end
            while len(trimmed_word) > 1 and trimmed_word[-1] in self.__settings["trim_punctuation_characters"] + [" "]:
                # Removes the last character
                trimmed_word = trimmed_word[:-1]
            # Adds the another poissible answer
            acceptable_answers.append(trimmed_word)
        if self.__settings["optional_answer_in_parentheses"]:
            acceptable_answers += [self.remove_nested_parentheses(x) for x in acceptable_answers]
            acceptable_answers += [x.replace("(", "").replace(")", "") for x in acceptable_answers]
        # Adds the cleaned verstions of the acceptable answers
        acceptable_answers += [self.clean_word(x) for x in acceptable_answers]
        # Is the answer correct
        return answ in acceptable_answers

    def clean_word(self, word):
        """
        Removes the unncesary whitespace characters from the string.
            And changes the case if nessesary.

        :param word: string, the input to be cleaned
        :return string, the cleaned string
        """
        # Clears the extra whitespace characters from the string
        word = re.sub('\s{2,}', ' ', word)
        # Removes the extras spaces from the begining and end
        word = word.strip()
        # If the answers are not case sensitive
        if not self.__settings["case_sensitive_answers"]:
            # Changes the word to lowercase
            word = word.lower()
        # The cleaned word
        return word

    def remove_nested_parentheses(self, input_string):
        # Define a regular expression pattern to match the innermost parentheses and their contents
        pattern = r'\([^()]*\)'
        
        # Repeatedly find and remove the innermost parentheses until none are left
        while re.search(pattern, input_string):
            input_string = re.sub(pattern, '', input_string)
        
        return input_string

    def save_statistics(self):
        with open(self.__settings["statistics_file"], mode="a") as my_file:
            content = []
            content.append(datetime.now())
            content.append(time.time() - self.__practice_time)
            content.append(self.__settings['wordlist_file'])
            content.append(self.__mode)
            #content.append(self.__settings["ques_lang"])
            content.append(self.__settings["ques_langs"])
            content.append(self.__settings["answ_lang"])
            try:
                acc = self.__number_of_correct_answers / (self.__number_of_correct_answers+self.__number_of_incorrect_answers)
            except:
                acc = 0
            content.append(acc)
            my_file.write(";".join(str(x) for x in content) + "\n")

    def learn_mode_end(self):
        """
        The end of the lear mode, statistics message.
        """
        # Resets the ansked question indecies
        self.__question_indices = list(range(self.__number_of_words))
        # Clears the unnecessary widgets
        self.clear_buttons()
        # Shows all the tabs
        self.enable_all_tabs()
        # Gets the current time
        practice_time = time.time() - self.__practice_time
        # Save statistics
        self.save_statistics()
        # Resets the time
        self.__practice_time = -1
        # The number of correct answers
        cor_n = self.__number_of_correct_answers
        # The number of incorrect answers
        incor_n = self.__number_of_incorrect_answers
        # The statistics lable
        self.__congrat_label = ttk.Label(
            self.__parent_tab, text =f"You have learnt all the phrases!\n"
                                    f"Your accuracy in this round was: "
                                    f"{cor_n}/{cor_n+incor_n}"
                                    f"={cor_n / (cor_n + incor_n) * 100:.0f}%.\n"
                                    f"You have practiced for "
                                    f"{practice_time / 60:.0f} minutes.",
                                    font = FONTS["p"])
        # Puts the label onto the window
        self.__congrat_label.grid(column = 0, row = 1)
        # Resets the number of correct answers
        self.__number_of_correct_answers = 0
        # Resets the number of correct answers
        self.__number_of_incorrect_answers = 0
        if self.__mode == "flashcards":
            # Restart button
            self.__flashcards_start_button = ttk.Button(
                self.__parent_tab, text = "Restart", command = self.start_timer)
            # Puts the button onto the window
            self.__flashcards_start_button.grid(column = 0, row = 2, columnspan = 2)
            # Sets the focus
            self.__flashcards_start_button.focus()
        elif self.__mode == "write":
            # Restart button
            self.__write_start_button = ttk.Button(
                self.__parent_tab, text = "Restart", command = self.start_timer)
            # Puts the button onto the window
            self.__write_start_button.grid(column = 0, row = 2, columnspan = 2)
            # Sets the focus
            self.__write_start_button.focus()
        # Binds the return key
        self.__main_window.bind('<Return>', self.start_timer)

    def correct_answer(self, event = None):
        """
        When the answer is correct.

        :param event: event, the click event, necessary.
        """
        # Increases the correct answer counter
        self.__number_of_correct_answers += 1
        # Removes the unncecesary widgets
        self.clear_buttons()
        # Removes the answered question
        self.__current_question_indecies.remove(self.__current_index)
        if self.__mode == "flashcards":
            # Next question
            self.flashcards_mode_flashcards()
        elif self.__mode == "write":
            # Next question
            self.write_mode_write()

    def incorrect_answer(self, event = None):
        """
        When the answer is incorrect.

        :param event: event, the click event, necessary.
        """
        # Increases the incorrect answer counter
        self.__number_of_incorrect_answers += 1
        # Removes the unncecesary widgets
        self.clear_buttons()
        # When to correct the mistakes
        if self.__settings["correct_mistakes"] == "round":
            # If there is more than on remaining question
            if len(self.__current_question_indecies) > 1:
                prew_first_elemnt = self.__current_question_indecies[0]
                # Shuffles the questions so that the next time cannot be the
                #   same question
                while self.__current_question_indecies[0] == prew_first_elemnt:
                    random.shuffle(self.__current_question_indecies)
        elif self.__settings["correct_mistakes"] == "end":
            # Removes the answered question
            self.__current_question_indecies.remove(self.__current_index)
            # Adds the question to the mistakes list
            self.__mistake_indecies.append(self.__current_index)

        if self.__mode == "flashcards":
            # Next question
            self.flashcards_mode_flashcards()
        elif self.__mode == "write":
            # Next question
            self.write_mode_write()

    def clear_list(self):
        """
        Deletes the widgets which correspont to a list:
            tree, scrollbar, header
        """
        # Goes through all the widgets
        for i in range(3):
            # Delete the widget
            self.delete_widget(self.__list[i])
        # Clears all the other widget
        self.clear_buttons()

    def clear_buttons(self):
        """
        Cleas all the unncesary widgets from the window.
        """
        if self.__mode == "flashcards":
            # The flashcards mode is not active
            self.__flashcards_keyboard_active = False
            # Flashcard
            self.delete_widget(self.__flashcard_button)
            # Correct btn
            self.delete_widget(self.__flashcards_correct_button)
            # Incorrect btn
            self.delete_widget(self.__flashcards_incorrect_button)
            # Start btn 2
            self.delete_widget(self.__flashcards_start_button2)
            # Start btn
            self.delete_widget(self.__flashcards_start_button)
            # Unbinds the return key
            self.unbind_event('<Return>', self.flashcards_mode_flashcards)
        elif self.__mode == "write":
            # Unbinds the return key
            self.unbind_event('<Return>', self.write_check_anwer)
            # Unbinds the return key
            self.unbind_event('<Return>', self.write_mode_write)
            # Start btn 2
            self.delete_widget(self.__write_start_button2)
            # Start btn
            self.delete_widget(self.__write_start_button)
            # Question label
            self.delete_widget(self.__write_question_label)
            # Answer entry
            self.delete_widget(self.__write_answer_entry)
            # Check btn
            self.delete_widget(self.__write_check_button)
            # Scrollbar
            self.delete_widget(self.__write_answer_entry_scrollbar)
            # Answer label
            self.delete_widget(self.__write_correct_answer_label)
            # Next btn
            self.delete_widget(self.__write_next_button)
            #self.__write_answer_entry.tag_add("INCORRECT", "1.0", "end")
            #self.__write_answer_entry.tag_remove("INCORRECT", "1.0", "end")
        # Unbinds return key
        self.unbind_event('<Return>', self.start_timer)
        # Statistics label
        self.delete_widget(self.__congrat_label)

    def delete_widget(self, widget):
        """
        Deletes a widget if it exists.

        :param widget: tkinter widget, the widget to be deleted
        :return bool, if the widget existed and the delition is successful
        """
        # Tries to delet it
        try:
            # It it exists
            if widget:
                # Destroies it
                widget.destroy()
                return True
        # If it does not exist
        except AttributeError:
            return False

    def unbind_event(self, key, func):
        """
        Unbinds a key from a function.

        :param key: string, the key from which it it unbinded
        :param func: function, function to be unbind
        :return bool, if the unbinding is successful
        """
        # Tries to unbind it
        try:
            # Unbinds it
            self.__main_window.unbind(key, func)
            return True
        # If it was not binded
        except TypeError:
            return False

    def print_word_list(self, headers, indecies, parent, row = 3, header_text = "In this round you will practice these phrases:", columnspan = 1):
        """
        Returnes a wordlist to be printed.

        :param headers: list of strings, which languages to print
        :param indecies: list of ints, which word indecies to print
        :param parent: tkinter widget, to whitch widget should it print
        :param row: int=3, in which row in the grid should it print the table
        :param header_text: string, the header of the table
        :return tuple of 3 tkinter widgets,
            the tree (the table), scrollbar, and the header label
        """
        # The label
        label = None
        if header_text:
            # Header label
            label = ttk.Label(parent, text = header_text, font = FONTS["p"])
            # Puts the header onto the grid
            label.grid(column = 0, row = row)
        # Gets the list
        tree, scrollbar = self.get_list(headers, indecies, parent)
        # Puts the tree onto the window
        tree.grid(row =row + 1, column = 0, sticky = 'nsew', columnspan=columnspan)
        # Puts the scrollbar onto the window
        scrollbar.grid(row = row + 1, column = 1, sticky = 'nse')
        # Sets the rowheight to expand
        parent.rowconfigure(row + 1, weight = 1)
        # Returns the widgets
        return tree, scrollbar, label

    def flashcard_button(self):
        """
        Flips the flashcard - shows the qeustion
            in the question or answer language
        """
        self.__flashcard_show_question = not self.__flashcard_show_question
        if self.__flashcard_show_question:
            text = (self.__settings["separator"]+"\n").join([
                self.__word_list[x][self.__current_index] for x in self.__settings["ques_langs"]
            ])
        else:
            text = self.__word_list[self.__settings["answ_lang"]][self.__current_index]
        self.__flashcard_button.configure(text = text)
        """# If it currently shows the question in the question language
        if self.__flashcard_shown_language == self.__settings["ques_lang"]:
            # It sets to show in the answer language
            self.__flashcard_shown_language = self.__settings["answ_lang"]
        else:
            # It sets to show in the question language
            self.__flashcard_shown_language = self.__settings["ques_lang"]
        # Sets the text
        self.__flashcard_button.configure(
            text =self.__word_list[self.__flashcard_shown_language][self.__current_index])"""

    def quit(self):
        """
        Quit from the GUI.
        """
        # Closes the window
        self.__main_window.destroy()

    def open_statistics_file(self):
        # Clears the error messate
        self.set_message()
        # The allowed file types
        file_types = (('tabular files', '*.csv'), ('text files', '*.txt'))
        # The file dialog
        my_file_name = filedialog.askopenfilename(filetypes = file_types)
        self.__settings["statistics_file"] = my_file_name
        self.__statistics_file_label.configure(text=f"Current file: {self.__settings['statistics_file']}")

    def open_file(self):
        """
        Opens the wordlist file and reads its content.
        Shows the error message if the file is incorrect.

        :return None
        """
        # Clears the error messate
        self.set_message()
        # The allowed file types
        file_types = (('tabular files', '*.csv'), ('text files', '*.txt'))
        # The file dialog
        my_file_name = filedialog.askopenfilename(filetypes = file_types)
        self.__settings["wordlist_file"] = my_file_name
        try:
            # Opens the file, using UTF-8 encoding
            with open(my_file_name, "r", encoding= "utf8") as my_file:
                # The separator character
                separator_char = self.__settings["separator"]
                # If it can get the sep. char. from the GUI
                if self.__separator.get() != "":
                    # It gets the separator character
                    separator_char = self.__separator.get()
                # Stores the lines and removes the new line characters
                lines = [x.strip() for x in my_file.readlines() if x.strip() != ""]
                # If the file is empty
                if len(lines) == 0:
                    # Shows the error message
                    self.set_message(
                        "error", "The file must have a header row! Try another file!")
                    return
                # If there are no words in the file
                elif len(lines) == 1:
                    # Shows the error message
                    self.set_message(
                        "error", "There must be phrases in the file! Try another file!")
                    return
                
                # The zeroth line contains the languages
                self.__languages = lines[0].split(separator_char)
                # Cheks if one language is in the header multiple times
                if sorted(list(set(self.__languages))) != sorted(self.__languages):
                    # Shows the error message
                    self.set_message(
                        "error", "The same language cannot be twice in the file header! Try another file!")
                    return
                # Add the languages to the word list dictionary
                for lang in self.__languages:
                    self.__word_list[lang] = []

                # Adds the words to the word list
                for line in lines[1:]:
                    # Splits the line
                    word_line = line.split(separator_char)
                    # If the line has correct number of phrases
                    if len(self.__languages) == len(word_line):
                        # Go through the line
                        for i in range(len(word_line)):
                            # Adds the word to the wordlist dict
                            self.__word_list[self.__languages[i]].append(word_line[i])
                    else:
                        # Shows the error message
                        self.set_message("error", 
                                         f"Error in reading the file: in line "
                                         f"'{line}' the number of "
                                         f"terms is incorrect. Try another file!")
                        self.__word_list = {}
                        return
            self.setings_after_new_word_list()        

        except FileNotFoundError:
            # Shows the error message
            self.set_message(
                "error", "The file was not found! Try another file!")
            return
        except:
            # Shows the error message
            self.set_message(
                "error", f"There was an error in the file opening! Try another file!")
            return

    def setings_after_new_word_list(self):
        self.__tabs.tab(1, state = "disabled")
        self.__tabs.tab(2, state = "disabled")
        self.__tabs.tab(3, state = "disabled")
        self.__tabs.tab(4, state = "disabled")
        # Number of words
        self.__number_of_words = len(self.__word_list[self.__languages[0]])
        # Shows the info message
        self.set_message(
            "info", f"{self.__number_of_words} terms have succesfully read from the file.")
        warning_texts = []
        for lang in self.__word_list:
            duplicates = self.find_duplicates(self.__word_list[lang])
            if duplicates:
                warning_texts += [f"{lang}: {duplicates}"]
        if len(warning_texts) != 0:
            self.set_message(
                "warning", f"There are duplicates in the file: {', '.join(warning_texts)}")
        # Shows the error message
        self.set_message(
            "error", "You have to save the initial settings to start practicing!")
        # Sets the available languages
        self.__ques_lang_clicled_items = [IntVar() for _ in range(len(self.__languages))]
        self.__question_mb.menu = Menu(self.__question_mb, tearoff = 0)
        self.__question_mb["menu"] = self.__question_mb.menu
        for i in range(len(self.__languages)):
            self.__question_mb.menu.add_checkbutton(label=self.__languages[i], variable=self.__ques_lang_clicled_items[i])
        """self.__ques_lang_btn.set_menu(
            self.__languages[0], *self.__languages)"""
        # Sets the available languages
        self.__answ_lang_btn.set_menu(
            self.__languages[0], *self.__languages)
        self.__translate_btn.set_menu(
            self.__languages[0], *self.__languages)
        # Sets the question indecies
        self.__question_indices = list(range(self.__number_of_words))
        # Updates the list tab
        self.update_list_tab()

    def find_duplicates(self, strings):
        seen = set()
        duplicates = set()

        for string in strings:
            if string in seen:
                duplicates.add(string)
            else:
                seen.add(string)

        if duplicates:
            return list(duplicates)
        else:
            return None

    def set_message(self, msg_type= "", text = ""):
        """
        Sets the content of the error and the info label.

        :param msg_type: string, which label to change, if empty both
        :param text: string, the new conten of the label
        """
        # Error label
        if msg_type == "error" or msg_type == "":
            # Sets the text
            self.__error_label.configure(text = text)
        # Info label
        if msg_type == "info" or msg_type == "":
            # Sets the text
            self.__info_label.configure(text = text)
        # Warning label
        if msg_type == "warning" or msg_type == "":
            # Sets the text
            self.__warning_label.configure(text = text)
        # Translate error label
        if msg_type == "translate_error" or msg_type == "":
            # Sets the text
            self.__translate_error_label.configure(text = text)

    def save_settings(self):
        """
        Saves the settings from the settings tab to the
            settings dictionary.
        """
        # Clears the messages
        self.set_message()
        # The separator cannot be empty
        if self.__separator.get() == "":
            # Cancels the setting chages
            self.cancel_settings()
            # Sets the error message
            self.set_message("error", "The separator cannot be empty!")
            return
        else:
            self.__settings["separator"] = self.__separator.get()
        # The batch size has to be a nonnegative int
        try:
            batch_size = int(self.__batch_size.get())
            # If it is negative
            if batch_size < 0:
                # Cancels the setting chages
                self.cancel_settings()
                # Sets the error message
                self.set_message("error", "The batch size must be nonegative!")
                return
        # If it is not int
        except ValueError:
            # Cancels the setting chages
            self.cancel_settings()
            # Sets the error message
            self.set_message("error", "The batch size must be an ineger!")
            return
        # If a language is not selected
        is_language_selected = False
        for i in range(len(self.__ques_lang_clicled_items)):
            if self.__ques_lang_clicled_items[i].get():
                is_language_selected = True
        if not is_language_selected:
            # Cancels the setting chages
            self.cancel_settings()
            # Sets the error message
            self.set_message("error", "You have to select a question language!")
            return
        """if self.__ques_lang_clicled.get() == "-":
            # Cancels the setting chages
            self.cancel_settings()
            # Sets the error message
            self.set_message(
                "error", "You have to choose the question language!")
            return"""
        # If a language is not selected
        if self.__answ_lang_clicled.get() == "-":
            # Cancels the setting chages
            self.cancel_settings()
            # Sets the error message
            self.set_message(
                "error", "You have to choose the answer language!")
            return
        if self.__settings["statistics_file"] == "-":
            # Cancels the setting chages
            self.cancel_settings()
            # Sets the error message
            self.set_message(
                "error", "You have to choose a statistics file!")
            return


        # Sets the settings from the GUI
        """self.__settings = {
            "separator": self.__separator.get(),
            "shuffle": True if self.__shuffle_clicled.get() == "True" else False,
            "ques_lang": self.__ques_lang_clicled.get(),
            "answ_lang": self.__answ_lang_clicled.get(),
            "batch_size": batch_size,
            "correct_mistakes": self.__correct_clicled.get(),
            "repeat_until_correct": True if self.__repeat_until_correct_clicled.get() == "True" else False,
            "case_sensitive_answers": True if self.__case_sensitive_answers_clicled.get() == "True" else False,
            "trim_punctuation_characters": list(self.__trim_characters.get()),
            "trim_punctuation": self.__trim_position_clicled.get(),
            "optional_answer_in_parentheses": True,
            "speak_enabled": True,
            "volume": VOLUME,
            "statistics_file": "statistics.csv"
        }"""
        self.__settings["separator"] = self.__separator.get()
        self.__settings["shuffle"] = True if self.__shuffle_clicled.get() == "True" else False
        #self.__settings["ques_lang"] = self.__ques_lang_clicled.get()
        self.__settings["ques_langs"] = [self.__languages[i] for i in range(len(self.__languages)) if self.__ques_lang_clicled_items[i].get()]
        self.__settings["answ_lang"] = self.__answ_lang_clicled.get()
        self.__settings["batch_size"] = batch_size
        self.__settings["correct_mistakes"] = self.__correct_clicled.get()
        self.__settings["repeat_until_correct"] = True if self.__repeat_until_correct_clicled.get() == "True" else False
        self.__settings["case_sensitive_answers"] = True if self.__case_sensitive_answers_clicled.get() == "True" else False
        self.__settings["trim_punctuation_characters"] = list(self.__trim_characters.get())
        self.__settings["trim_punctuation"] = self.__trim_position_clicled.get()
        self.__settings["optional_answer_in_parentheses"] = True if self.__optional_answers_clicled.get() == "True" else False
        self.__settings["speak_enabled"] = True if self.__speak_enabled_clicled.get() == "True" else False
        self.__settings["volume"] = self.__volume.get() / 100
        
        # Shows all tabs
        self.enable_all_tabs()

    def enable_all_tabs(self):
        """
        Enables all the tabs.
        """
        # Settings tab enabled
        self.__tabs.tab(0, state = "normal")
        # List tab enabled
        self.__tabs.tab(1, state = "normal")
        # Flashcards tab enabled
        self.__tabs.tab(2, state = "normal")
        # Write tab enabled
        self.__tabs.tab(3, state = "normal")
        if TRANSLATE_AVAILABELE:
            # Translate tab enabled
            self.__tabs.tab(4, state = "normal")
        else:
            self.__tabs.tab(4, state = "disabled")

    def cancel_settings(self):
        """
        Cancels the setting chages.
        """
        # Cleares the error message
        self.set_message()
        # Separator
        self.__separator.delete(0, END)
        self.__separator.insert(0, self.__settings["separator"])
        # Shuffle
        self.__shuffle_clicled.set(
            "True" if self.__settings["shuffle"] else "False")
        # Question language
        for i in range(len(self.__ques_lang_clicled_items)):
            if self.__languages[i] in self.__settings["ques_langs"]:
                self.__ques_lang_clicled_items[i].set(1)
            else:
                self.__ques_lang_clicled_items[i].set(0)
        #self.__ques_lang_clicled.set(self.__settings["ques_lang"])
        # Answer language
        self.__answ_lang_clicled.set(self.__settings["answ_lang"])
        # Batch size
        self.__batch_size.delete(0, END)
        self.__batch_size.insert(0, self.__settings["batch_size"])
        # Correct mistakes
        self.__correct_clicled.set(self.__settings["correct_mistakes"])
        # Case sensitive answers
        self.__case_sensitive_answers_clicled.set(
            "True" if self.__settings["case_sensitive_answers"] else "False")
        # Repeat until correct
        self.__repeat_until_correct_clicled.set(
            "True" if self.__settings["repeat_until_correct"] else "False")
        # Trim characters
        self.__trim_characters.delete(0, END)
        self.__trim_characters.insert(0, "".join(
            self.__settings["trim_punctuation_characters"]))
        # Trim punctuation
        self.__trim_position_clicled.set(self.__settings["trim_punctuation"])
        # Optional answers
        self.__optional_answers_clicled.set(
            "True" if self.__settings["optional_answer_in_parentheses"] else "False")
        # Speak enabled
        self.__speak_enabled_clicled.set(
            "True" if self.__settings["speak_enabled"] else "False")
        self.__volume.set(self.__settings["volume"]*100)

    def update_list_tab(self):
        """
        Updates the content of the list tab.
        """
        # Prints the word list
        self.print_word_list(self.__languages, range(
            self.__number_of_words), self.__list_tab, 1, None)
        # Sets the columnwidth
        self.__list_tab.columnconfigure(0, weight = 1)

        # Translate tab
        # Prints the word list
        self.print_word_list(self.__languages, range(
            self.__number_of_words), self.__translate_tab, 20, None, 2)
        # Sets the columnwidth
        self.__translate_tab.columnconfigure(0, weight = 1)
        self.__translate_tab.columnconfigure(1, weight = 1)

    def get_list(self, headers, indecies, parent):
        """
        Returnes the components of a wordlist.

        :param headers: list of strings, which languages to print
        :param indecies: list of ints, which word indecies to print
        :param parent: tkinter widget, to whitch widget should it print
        :return tuple of 2 tkinter widgets,
            the tree (the table), scrollbar
        """
        # Columns
        columns = tuple(headers)
        # Table
        tree = ttk.Treeview(parent, columns = columns, show = 'headings')
        # Sets the headers
        for lang in columns:
            tree.heading(lang, text = lang)
        # Sets the content of the rows
        for i in indecies:
            # Content of a row
            content = tuple([self.__word_list[lang][i] for lang in columns])
            # Adds the content
            tree.insert('', END, values = content)
        # Adds a scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=VERTICAL, command = tree.yview)
        # Sets a scrollbar
        tree.configure(yscroll = scrollbar.set)
        # Returns the widgets
        return tree, scrollbar

    def __del__(self):
        if self.__practice_time != -1:
            self.save_statistics()
        try:
            data = pd.read_csv(self.__settings["statistics_file"], sep=";")
            # Get today's date
            today_date = datetime.now().date()
            # Converts the column to datatime type
            data['Date'] = pd.to_datetime(data['Date'])
            # Filter rows based on today's date
            today_rows = data[data['Date'].dt.date == today_date]

            today_practice = np.sum(today_rows["Time"]) / 3600
            all_practice = np.sum(data["Time"]) / 3600

            d = (TARGET_PRACTICE - all_practice) / today_practice

            print(f"Today you have practiced {today_practice*60:.0f} minutes.")
            print(f"All practice: {all_practice:.1f}/{TARGET_PRACTICE} hours.")
            print(f"At this rate it will take {d:.0f} days to learn the language.")
        except Exception as e:
            print("The statistics file cannot be opened!", e)
        print("bye")

def main():
    # Creates the GUI
    app = GUI()

if __name__ == "__main__":
    main()
