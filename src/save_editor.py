import random
import sys
from enum import Enum

from colorama import Fore, just_fix_windows_console

just_fix_windows_console()

from edits import *
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


def main():
    save_state = None
    try:
        next_state = state_start()
        while True:
            match next_state:
                case STATES.OPTIONS_START:
                    previous_state = STATES.OPTIONS_START
                    next_state = state_start(False)
                case STATES.OPTIONS_EDIT_START:
                    previous_state = STATES.OPTIONS_START
                    next_state = state_options_edit_start(previous_state)
                case STATES.OPTIONS_EDIT_AUTO_DISCOVER_SAVES:
                    previous_state = STATES.OPTIONS_EDIT_START
                    save_path = state_auto_discover_saves()
                    save_state = SaveState(save_path)
                    print(Fore.GREEN + "[+]" + Fore.RESET + " Save state loaded.")
                    next_state = STATES.OPTIONS_EDIT
                case STATES.OPTIONS_EDIT_MANUAL_SAVE:
                    previous_state = STATES.OPTIONS_EDIT_START
                    save_path = state_manual_save()
                    save_state = SaveState(save_path)
                    print(Fore.GREEN + "[+]" + Fore.RESET + " Save state loaded.")
                    next_state = STATES.OPTIONS_EDIT
                case STATES.OPTIONS_RESTORE:
                    previous_state = STATES.OPTIONS_START
                    next_state = state_options_restore(previous_state)
                case STATES.OPTIONS_RESTORE_AUTO_DISCOVER_BACKUPS:
                    previous_state = STATES.OPTIONS_RESTORE
                    backup_path = state_auto_discover_backups()
                    restore_save(backup_path)
                    print(Fore.GREEN + "[+]" + Fore.RESET + " Backup was restored.")
                    next_state = STATES.OPTIONS_START
                case STATES.OPTIONS_RESTORE_MANUAL_BACKUP:
                    previous_state = STATES.OPTIONS_RESTORE
                    backup_path = state_manual_backup()
                    restore_save(backup_path)
                    print(Fore.GREEN + "[+]" + Fore.RESET + " Backup was restored.")
                    next_state = STATES.OPTIONS_START
                case STATES.OPTIONS_EDIT:
                    previous_state = STATES.OPTIONS_EDIT_START
                    next_state = state_options_edit(previous_state)
                    if next_state == previous_state:
                        save_state.rollback()
                        del save_state
                case STATES.OPTIONS_EDIT_DOORS:
                    previous_state = STATES.OPTIONS_EDIT
                    key, value = state_edit_doors(save_state)
                    save_state.set_door(key, value)
                    print(Fore.GREEN + "[+]" + Fore.RESET + " Door state set.")
                    next_state = STATES.OPTIONS_EDIT
                case STATES.OPTIONS_EDIT_TIME:
                    previous_state = STATES.OPTIONS_EDIT
                    key, value = state_edit_time(save_state)
                    save_state.set_time(key, value)
                    print(Fore.GREEN + "[+]" + Fore.RESET + " Time value set.")
                    next_state = STATES.OPTIONS_EDIT
                case STATES.OPTIONS_EDIT_RESOURCE:
                    previous_state = STATES.OPTIONS_EDIT
                    key, value = state_edit_resource(save_state)
                    save_state.set_resource(key, value)
                    print(Fore.GREEN + "[+]" + Fore.RESET + " Resource value set.")
                    next_state = STATES.OPTIONS_EDIT
                case STATES.OPTIONS_EDIT_THOUGHTS:
                    previous_state = STATES.OPTIONS_EDIT
                    if state_edit_thoughts():
                        save_state.set_all_unknown_and_forgotten_thoughts()
                        print(
                            Fore.GREEN
                            + "[+]"
                            + Fore.RESET
                            + " All unknown and forgotten thought states set."
                        )
                    next_state = STATES.OPTIONS_EDIT
                case STATES.OPTIONS_EDIT_CHAR_SHEET:
                    previous_state = STATES.OPTIONS_EDIT
                    key, value = state_edit_char_sheet(save_state)
                    save_state.set_char_sheet_stat(key, value)
                    print(
                        Fore.GREEN + "[+]" + Fore.RESET + " Character sheet stat set."
                    )
                    next_state = STATES.OPTIONS_EDIT
                case STATES.OPTIONS_EDIT_ROLLBACK:
                    previous_state = STATES.OPTIONS_EDIT
                    save_state.rollback()
                    print(Fore.GREEN + "[+]" + Fore.RESET + " All changes rolled back.")
                    next_state = STATES.OPTIONS_START
                case STATES.OPTIONS_EDIT_COMMIT:
                    previous_state = STATES.OPTIONS_EDIT
                    save_state.commit()
                    print(
                        Fore.GREEN
                        + "[+]"
                        + Fore.RESET
                        + " All changes committed to disk."
                    )
                    next_state = STATES.OPTIONS_START
    except (KeyboardInterrupt, Exception):
        if save_state is not None:
            save_state.rollback()
        raise


if __name__ == "__main__":
    main()
