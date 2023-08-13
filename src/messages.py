from colorama import Fore, just_fix_windows_console

just_fix_windows_console()

PROMPTS = [
    "The program patiently awaits your command: ",
    "The machine hums beneath your hands, expectant: ",
    "You decide what to do: ",
]

DISCLAIMER = (
    Fore.MAGENTA
    + "DISCLAIMER: I have tried to implement safety measure to make sure your saves don't get lost while using this.\n"
    "However, this program is still rough around the edges and error handling is not ... meticulous.\n"
    "I will not be responsible for any corrupted or lost saves. Make a backup of your saves beforehand and be careful when modifying the values.\n"
    + Fore.RESET
)

WELCOME = (
    Fore.GREEN
    + "\n[Interfacing (Trivial): Success]"
    + Fore.RESET
    + "\n\tYou can see a welcome message while opening the program explaining that the purpose of the program is to edit the save files of some game called 'Disco Elysium'."
    + Fore.GREEN
    + "\n[Reaction Speed (Medium): Success]"
    + Fore.RESET
    + "\n\tWhat an odd name for a game."
    + Fore.GREEN
    + "\n[Inland Empire (Easy): Success]"
    + Fore.RESET
    + "\n\tSounds mysterious."
    + Fore.GREEN
    + "\n[Logic (Hard): Success]"
    + Fore.RESET
    + "\n\tSounds ... impossible?"
    + Fore.GREEN
    + "\n[Electrochemistry (Trivial): Success]"
    + Fore.RESET
    + "\n\tSOUNDS PRETTY &@*#ing DISCO TO ME! YEAH!"
    + Fore.RED
    + "\n[Conceptualization (Impossible): Failure]"
    + Fore.RESET
    + "\n\tAre you living in a simulation? Are you in this ... 'game'? You shake away the thought before anything concrete starts to form."
    + Fore.GREEN
    + "\n[Perception (Trivial): Success]"
    + Fore.RESET
    + "\n\tThe options are displayed for you on the small screen:\n"
)

OPTIONS_START = (
    Fore.YELLOW
    + "1."
    + Fore.RESET
    + " Edit a save file.\n"
    + Fore.YELLOW
    + "2."
    + Fore.RESET
    + " Restore a previous backup.\n"
    + Fore.YELLOW
    + "3."
    + Fore.RESET
    + " Exit the program.\n"
)

OPTIONS_EDIT_START = (
    "You need to identify a save file to edit first. Would you like:\n"
    + Fore.YELLOW
    + "1."
    + Fore.RESET
    + " For the program to attempt to automatically identify all of your save files from a default location.\n"
    + Fore.YELLOW
    + "2."
    + Fore.RESET
    + " To provide the exact path to a specific save file manually.\n"
    + Fore.YELLOW
    + "3."
    + Fore.RESET
    + " [GO BACK]\n"
)

OPTIONS_EDIT = (
    "More features may be implemented later but for now here's a list of things you can alter in your save file:\n"
    + Fore.YELLOW
    + "1."
    + Fore.RESET
    + " Open/Close doors.\n"
    + Fore.YELLOW
    + "2."
    + Fore.RESET
    + " Set in-game time of day.\n"
    + Fore.YELLOW
    + "3."
    + Fore.RESET
    + " Set value for a resource.\n"
    + Fore.YELLOW
    + "4."
    + Fore.RESET
    + " Set all unknown thoughts as known (so you can internalize any of them).\n"
    + Fore.YELLOW
    + "5."
    + Fore.RESET
    + " Set value for a stat in the character sheet.\n"
    + Fore.YELLOW
    + "6."
    + Fore.RESET
    + " Rollback current modifications.\n"
    + Fore.YELLOW
    + "7."
    + Fore.RESET
    + " Commit current modifications to disk.\n"
    + Fore.YELLOW
    + "8."
    + Fore.RESET
    + " [GO BACK]\n"
)

OPTIONS_RESTORE = (
    "Would you like:\n"
    + Fore.YELLOW
    + "1."
    + Fore.RESET
    + " To provide the exact path to a specific backup file manually for restoration.\n"
    + Fore.YELLOW
    + "2."
    + Fore.RESET
    + " Have the program discover all of the present backups for you from the default location and let you choose which one you wish to restore.\n"
    + Fore.YELLOW
    + "3."
    + Fore.RESET
    + " [GO BACK]\n"
)
