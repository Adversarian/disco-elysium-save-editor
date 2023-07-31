from utils import *
from edits import *
import random

PROMPTS = [
    "The program patiently awaits your command: ",
    "The machine hums beneath you, expectant: ",
    "You decide what to do: ",
]

DISCLAIMER = (
    "DISCLAIMER: I have tried to implement safety measure to make sure your saves don't get lost while using this.\n"
    "However, this program is still rough around the edges and error handling is not ... meticulous.\n"
    "I will not be responsible for any corrupted or lost saves. Make a backup of your saves beforehand and be careful when modifying the values.\n"
)

WELCOME = (
    "\n[Interfacing (Trivial): Success]\n\tYou can see a welcome message while opening the program explaining that the purpose of the program is to edit the save files of some game called 'Disco Elysium'."
    "\n[Reaction Speed (Medium): Success]\n\tWhat an odd name for a game."
    "\n[Inland Empire (Easy): Success]\n\tSounds mysterious."
    "\n[Logic (Hard): Success]\n\tSounds ... impossible?"
    "\n[Electrochemistry (Trivial): Success]\n\tSOUNDS PRETTY &@*#ing DISCO TO ME! YEAH!"
    "\n[Conceptualization (Impossible): Failure]\n\tAre you living in a simulation? Are you in this ... 'game'? You shake away the thought before anything concrete starts to form."
    "\n[Perception (Trivial): Success]\n\tThe options are displayed for you on the small screen:\n"
)

OPTIONS_START = (
    "1. Edit a save file.\n" "2. Restore a previous backup.\n" "3. Exit the program.\n"
)

OPTIONS_EDIT_START = (
    "You need to identify a save file to edit first. Would you like:\n"
    "1. For the program to attempt to automatically identify all of your save files from a default location.\n"
    "2. To provide the exact path to a specific save file manually.\n"
    "3. [GO BACK]\n"
)

OPTIONS_EDIT = (
    "More features may be implemented later but for now here's a list of things you can alter in your save file:\n"
    "1. Open/Close doors.\n"
    "2. Set in-game time of day.\n"
    "3. Set value for a resource.\n"
    "4. Set all unknown thoughts as known (so you can internalize any of them).\n"
    "5. Rollback current modifications.\n"
    "7. Commit current modifications.\n"
    "8. [GO BACK]\n"
)

OPTIONS_RESTORE = (
    "Would you like:\n"
    "1. To provide the exact path to a specific backup file manually for restoration.\n"
    "2. Have the program discover all of the present backups for you from the default location and let you choose which one you wish to restore.\n"
    "3. [GO BACK]\n"
)


def get_prompt_msg():
    return PROMPTS[random.randint(0, len(PROMPTS) - 1)]


def get_input(cast_as=str, msg=""):
    return cast_as(input(msg))


def state_exit():
    exit(0)


def state_start(first_time):
    if first_time:
        print(DISCLAIMER)
    print(WELCOME)
    print(OPTIONS_EDIT_START)
    return get_input(int, get_prompt_msg())


def state_options_edit_start():
    print(OPTIONS_EDIT_START)
    return get_input(int, get_prompt_msg())


def state_auto_discover_saves():
    success, path = auto_discover()
    if not success:
        print(
            "Unable to discover save files. Please enter a path to the root of your save folder manually."
        )
        return get_input(str, get_prompt_msg())
    if success:
        print(f"Save files were discovered at {path}")
        parsed_saves = parse_saves(path)
        parsed_saves_int_map = {i: k for i, k in enumerate(parsed_saves.keys())}
        print("Which save file would you like to modify: ")
        pprint_dict(parsed_saves_int_map)
        choice = get_input(int)
        return parsed_saves[parsed_saves_int_map[choice]]


def state_edit_doors(save_state: SaveState):
    print("These are the doors whose in-game states can be altered: ")
    doors_int_map = {
        i: k
        for i, k in enumerate(MAPS["Doors"])
        if MAPS["Doors"][k] not in ["common_ancestor", "map"]
    }
    pprint_dict(doors_int_map)
    choice = get_input(int, "Which door would you like to modify: ")
    key = MAPS["Doors"][doors_int_map[choice]]
    current_door_state = save_state.get_door(key)
    choice = get_input(
        str,
        (
            f"The current state of the door is *{'Open' if current_door_state else 'Closed'}*."
            "What would you like to change it to (Open/Closed case insensitive): ",
        ),
    )
    assert choice.lower() in ["open", "closed"]
    value = True if choice.lower() == "open" else False
    return key, value


def state_options_edit():
    print(OPTIONS_EDIT)
    return get_input(int, get_prompt_msg())


def state_options_restore():
    print(OPTIONS_RESTORE)
    return get_input(int, get_prompt_msg())


def main():
    pass


if __name__ == "__main__":
    main()
