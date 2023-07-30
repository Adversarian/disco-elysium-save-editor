from utils import *
from edits import *
import random

PROMPTS = [
    "The program patiently awaits your command: ",
    "The keyboard looks at you, expectant: ",
    "You decide what to do: ",
]

WELCOME = (
    "\n[Interfacing (Trivial): Success]\n\tYou can see a welcome message while opening the program explaining that the purpose of the program is to edit the save files of some game called 'Disco Elysium'."\
    "\n[Reaction Speed (Medium): Success]\n\tWhat an odd name for a game."\
    "\n[Inland Empire (Easy): Success]\n\tSounds mysterious."\
    "\n[Logic (Hard): Success]\n\tSounds ... impossible?"\
    "\n[Electrochemistry (Trivial): Success]\n\tSOUNDS PRETTY &@*!%^# DISCO TO ME! YEAH!"\
    "\n[Conceptualization (Impossible): Failure]\n\tAre you living in a simulation? Are you in this ... 'game'? You shake away the thought before anything concrete starts to form."\
    "\n[Perception (Trivial): Success]\n\tThe options are displayed for you on the small screen:"
)

OPTIONS_START = (
    "1. Edit a save file.\n"\
    "2. Restore a previous backup.\n"\
    "3. Exit the program.\n"
)

OPTIONS_EDIT_START = (
    "You need to identify a save file to edit first. Would you like:\n"\
    "1. For the program to attempt to automatically identify all of your save files from a default location.\n"\
    "2. To provide the exact path to a specific save file manually.\n"\
    "3. [GO BACK]\n"
)

OPTIONS_EDIT = (
    "More features may be implemented later but for now here's a list of things you can alter in your save file:\n"\
    "1. Open/Close doors.\n"\
    "2. Set in-game time of day.\n"\
    "3. Set value for a resource.\n"\
    "4. Set all unknown thoughts as known (so you can internalize any of them).\n"\
    "5. Rollback current modifications.\n"\
    "6. [GO BACK]\n"\
)

OPTIONS_RESTORE = (
    "Would you like:\n"\
    "1. To provide the exact path to a specific backup file manually for restoration.\n"\
    "2. Have the program discover all of the present backups for you from the default location and let you choose which one you wish to restore.\n"\
    "3. "
)

def get_prompt_msg():
    return PROMPTS[random.randint(0, len(PROMPTS) - 1)]

def get_input(cast_as=str, msg=""):
    return cast_as(input(msg))
