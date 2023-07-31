from utils import *
from edits import *
import random
from enum import Enum

STATES = Enum(
    "STATES",
    [
        "OPTIONS_START",
        "OPTIONS_EDIT_START",
        "OPTIONS_EDIT",
        "OPTIONS_EDIT_AUTO_DISCOVER_SAVES",
        "OPTIONS_EDIT_MANUAL_SAVE",
        "OPTIONS_EDIT_DOORS",
        "OPTIONS_EDIT_TIME",
        "OPTIONS_EDIT_RESOURCE",
        "OPTIONS_EDIT_THOUGHTS",
        "OPTIONS_EDIT_ROLLBACK",
        "OPTIONS_EDIT_COMMIT",
        "OPTIONS_RESTORE",
    ],
)

PROMPTS = [
    "The program patiently awaits your command: ",
    "The machine hums beneath your hands, expectant: ",
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
    "6. Commit current modifications.\n"
    "7. [GO BACK]\n"
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


def state_start(first_time=True):
    if first_time:
        print(DISCLAIMER)
    print(WELCOME)
    print(OPTIONS_EDIT_START)
    choice = get_input(int, get_prompt_msg())
    assert choice in [1, 2, 3]
    match choice:
        case 1:
            return STATES.OPTIONS_EDIT_START
        case 2:
            return STATES.OPTIONS_RESTORE
        case 3:
            state_exit()


def state_options_edit_start(previous_state):
    print(OPTIONS_EDIT_START)
    choice = get_input(int, get_prompt_msg())
    assert choice in [1, 2, 3]
    match choice:
        case 1:
            return STATES.OPTIONS_EDIT_AUTO_DISCOVER_SAVES
        case 2:
            return STATES.OPTIONS_EDIT_MANUAL_SAVE
        case 3:
            return previous_state


def state_manual_save():
    return get_input(str, "Please enter the complete path to your save file.")


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
    choice = get_input(int, "Which door would you like to modify (Case SENSITIVE): ")
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


def state_edit_time(save_state: SaveState):
    key = "Minutes passed in Day"  #
    current_time_state = save_state.get_time(key)
    value = get_input(
        str,
        (
            f"The current time of day is *{current_time_state}*."
            "What would you like to change it to (formulate your input as hh:mm time, e.g. 04:20): "
        ),
    )
    # TODO: error handling
    return key, value


def state_edit_resource(save_state: SaveState):
    print("These are the in-game resources whose values you can edit:")
    resources_int_map = {
        i: k
        for i, k in enumerate(MAPS["Resources"])
        if MAPS["Resources"][k] not in ["common_ancestor", "map"]
    }
    pprint_dict(resources_int_map)
    choice = get_input(
        int, "Which resource would you like to modify (Case SENSITIVE): "
    )
    flag_money = resources_int_map[choice] == "Money"
    key = MAPS["Resources"][resources_int_map[choice]]
    current_resource_state = save_state.get_resource(key)
    if flag_money:
        current_resource_state = float(current_resource_state) / 10
        value = get_input(
            float,
            f"The current value of this resource is *{current_resource_state}*."
            "What would you like to change it to (please enter a floating point number with at most 2 decimals, e.g. 132.50): ",
        )
    else:
        value = get_input(
            int,
            f"The current value of this resource is *{current_resource_state}*."
            "What would you like to change it to (please enter an integer): ",
        )
    return key, value


def state_edit_thoughts():
    print(
        "This will change the state of all *forgotten* and *unknown* thoughts to *known*, allowing you to internalize them as you like. Would you like to proceed(Yes/No)?"
    )
    choice = get_input(str, get_prompt_msg())
    assert choice.lower() in ["yes", "no"]
    return True if choice.lower() == "yes" else False


def state_options_edit(previous_state):
    print(OPTIONS_EDIT)
    choice = get_input(int, get_prompt_msg())
    assert choice in [1, 2, 3, 4, 5, 6, 7]
    match choice:
        case 1:
            return STATES.OPTIONS_EDIT_DOORS
        case 2:
            return STATES.OPTIONS_EDIT_TIME
        case 3:
            return STATES.OPTIONS_EDIT_RESOURCE
        case 4:
            return STATES.OPTIONS_EDIT_THOUGHTS
        case 5:
            return STATES.OPTIONS_EDIT_ROLLBACK
        case 6:
            return STATES.OPTIONS_EDIT_COMMIT
        case 7:
            return previous_state


def state_options_restore(previous_state):
    print(OPTIONS_RESTORE)
    choice = get_input(int, get_prompt_msg())
    assert choice in [1, 2, 3]
    match choice:
        case 1:
            pass
        case 2:
            pass
        case 3:
            pass


def main():
    pass


if __name__ == "__main__":
    main()
