import random
import sys
from enum import Enum

from edits import *
from messages import *
from utils import *

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
        "OPTIONS_EDIT_CHAR_SHEET",
        "OPTIONS_EDIT_THOUGHTS",
        "OPTIONS_EDIT_ROLLBACK",
        "OPTIONS_EDIT_COMMIT",
        "OPTIONS_RESTORE",
        "OPTIONS_RESTORE_AUTO_DISCOVER_BACKUPS",
        "OPTIONS_RESTORE_MANUAL_BACKUP",
    ],
)


def get_prompt_msg():
    return PROMPTS[random.randint(0, len(PROMPTS) - 1)]


def get_input(cast_as=str, msg=""):
    return cast_as(input(msg))


def state_exit():
    get_input(str, "Press Enter to continue ...")
    sys.exit(0)


def state_start(first_time=True):
    if first_time:
        print(DISCLAIMER)
        print(WELCOME)
    print(OPTIONS_START)
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
    return get_input(str, "Please enter the complete path to your save file: \n")


def state_auto_discover_saves():
    success, path = auto_discover()
    if not success:
        print(
            Fore.RED
            + "[-]"
            + Fore.RESET
            + " Unable to discover save files. Please enter a path to the root of your save folder manually."
        )
        return get_input(str, get_prompt_msg())
    if success:
        print(Fore.GREEN + f"[+]" + Fore.RESET + " Default save path exists at {path}")
        parsed_saves = parse_saves(path)
        if parsed_saves:
            parsed_saves_int_map = {i: k for i, k in enumerate(parsed_saves.keys())}
            print("These are your save files:")
            pprint_dict(parsed_saves_int_map)
            choice = get_input(int, "Which one would you like to modify: ")
            return parsed_saves[parsed_saves_int_map[choice]]
        else:
            print(
                Fore.RED
                + "[-]"
                + Fore.RESET
                + " The save folder exists in the default location but no save files were discovered"
            )
            state_exit()


def state_edit_doors(save_state: SaveState):
    print("These are the doors whose in-game states can be altered: " + Fore.YELLOW)
    doors_int_map = {
        i: k for i, k in enumerate(MAPS["Doors"]) if k not in ["common_ancestor", "map"]
    }
    pprint_dict(doors_int_map)
    print(Fore.RESET)
    choice = get_input(int, "Which door would you like to modify (Case SENSITIVE): ")
    key = doors_int_map[choice]
    current_door_state = save_state.get_door(key)
    choice = get_input(
        str,
        (
            "The current state of the door is "
            + Fore.RED
            + f"{'Open' if current_door_state else 'Closed'}"
            + Fore.RESET
            + ". What would you like to change it to (Open/Closed case insensitive): ",
        ),
    )
    assert choice.lower() in ["open", "closed"]
    value = True if choice.lower() == "open" else False
    return key, value


def state_edit_time(save_state: SaveState):
    key = "Minutes Passed in Day"  # FC
    current_time_state = save_state.get_time(key)
    value = get_input(
        str,
        (
            "The current time of day is "
            + Fore.RED
            + f"{current_time_state}"
            + Fore.RESET
            + ". What would you like to change it to (formulate your input as hh:mm time, e.g. 04:20): "
        ),
    )
    # TODO: error handling
    return key, value


def state_edit_resource(save_state: SaveState):
    print("These are the in-game resources whose values you can edit:" + Fore.YELLOW)
    resources_int_map = {
        i: k
        for i, k in enumerate(MAPS["Resources"])
        if k not in ["common_ancestor", "map"]
    }
    pprint_dict(resources_int_map)
    print(Fore.RESET)
    choice = get_input(
        int, "Which resource would you like to modify (Case SENSITIVE): "
    )
    flag_money = resources_int_map[choice] == "Money"
    key = resources_int_map[choice]
    current_resource_state = save_state.get_resource(key)
    if flag_money:
        current_resource_state = float(current_resource_state) / 100
        value = get_input(
            float,
            "The current value of this resource is "
            + Fore.RED
            + f"{current_resource_state}"
            + Fore.RESET
            + ". What would you like to change it to (please enter a floating point number with at most 2 decimals, e.g. 132.50): ",
        )
    else:
        value = get_input(
            int,
            f"The current value of this resource is "
            + Fore.RED
            + f"{current_resource_state}"
            + Fore.RESET
            + ". What would you like to change it to (please enter an integer): ",
        )
    return key, value


def state_edit_char_sheet(save_state: SaveState):
    print(
        "These are the stats from the character sheet whose values you can edit:"
        + Fore.YELLOW
    )
    char_sheet_int_map = {
        i: k
        for i, k in enumerate(MAPS["Character Sheet"])
        if k not in ["common_ancestor", "map"]
    }
    pprint_dict(char_sheet_int_map)
    print(Fore.RESET)
    choice = get_input(int, "Which stat would you like to modify (Case SENSITIVE): ")
    key = char_sheet_int_map[choice]
    current_stat_value = save_state.get_char_sheet_stat(key)
    value = get_input(
        int,
        f"The current value of this resource is "
        + Fore.RED
        + f"{current_stat_value}"
        + Fore.RESET
        + ". What would you like to change it to (please enter an integer): ",
    )
    return key, value


def state_edit_thoughts():
    print(
        Fore.CYAN
        + "[!]"
        + Fore.RESET
        + " This will change the state of all *forgotten* and *unknown* thoughts to *known*, allowing you to internalize them as you like. Would you like to proceed(Yes/No)?"
    )
    choice = get_input(str, get_prompt_msg())
    assert choice.lower() in ["yes", "no"]
    return True if choice.lower() == "yes" else False


def state_options_edit(previous_state):
    print(OPTIONS_EDIT)
    choice = get_input(int, get_prompt_msg())
    assert choice in [1, 2, 3, 4, 5, 6, 7, 8]
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
            return STATES.OPTIONS_EDIT_CHAR_SHEET
        case 6:
            return STATES.OPTIONS_EDIT_ROLLBACK
        case 7:
            return STATES.OPTIONS_EDIT_COMMIT
        case 8:
            return previous_state


def state_auto_discover_backups():
    success, path = auto_discover()
    if not success:
        print(
            Fore.RED
            + "[-]"
            + Fore.RESET
            + " Unable to discover backup files. Please enter a path to the root of your backup folder manually."
        )
        return get_input(str, get_prompt_msg())
    if success:
        discovered_backups = discover_baks(path)
        if discovered_backups:
            discovered_backups_int_map = {
                i: k for i, k in enumerate(discovered_backups.keys())
            }
            print("These are your backups:")
            pprint_dict(discovered_backups_int_map)
            choice = get_input(int, "Which backup file would you like to restore: ")
            return discovered_backups[discovered_backups_int_map[choice]]
        else:
            print(
                Fore.RED
                + "[-]"
                + Fore.RESET
                + " The save folder exists in the default location but no backups were discovered"
            )
            state_exit()


def state_manual_backup():
    return get_input(str, "Please enter the complete path to your backup file: \n")


def state_options_restore(previous_state):
    print(OPTIONS_RESTORE)
    choice = get_input(int, get_prompt_msg())
    assert choice in [1, 2, 3]
    match choice:
        case 1:
            return STATES.OPTIONS_RESTORE_AUTO_DISCOVER_BACKUPS
        case 2:
            return STATES.OPTIONS_RESTORE_MANUAL_BACKUP
        case 3:
            return previous_state
