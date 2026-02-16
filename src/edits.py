import operator
from functools import reduce

from utils import *

MAPS = {
    "Doors": {
        "Whirling Door Tequila": ["Whirling Door Tequila"],
        "Bookstore Curtains": ["Bookstore Curtains"],
        "Whirling Door Klassje": ["Whirling Door Klassje"],
        "Whirling Door Bathroom Klassje": ["Whirling Door Bathroom Klassje"],
        "Door Apartment no dialogue(bathroom)": [
            "Door Apartment no dialogue(bathroom)"
        ],
        "Door Apartment 10": ["Door Apartment 10"],
        "Door Apartment 10 Open": ["Door Apartment 10 Open"],
        "common_ancestor": ["variousItemsHolder", "DoorStates"],
    },
    "Time": {
        "Minutes Passed in Day": ["dayMinutes"],
        "common_ancestor": ["sunshineClockTimeHolder", "time"],
    },
    "Resources": {
        "Skill Points": ["SkillPoints"],
        "Money": ["Money"],
        "Health Consumables": ["healingPools", "ENDURANCE"],
        "Morale Consumables": ["healingPools", "VOLITION"],
        "common_ancestor": ["playerCharacter"],
    },
    "All Thoughts": {
        "map": ["thoughtCabinetState", "thoughtListState"],
        "State": "state",
        "Time to Internalize": "timeLeft",
        "unknown_state": "UNKNOWN",
        "known_state": "KNOWN",
        "learned_state": "FIXED",
        "learning_state": "COOKING",
        "forgotten_state": "FORGOTTEN",
    },
    "Character Sheet": {
        "Intellect": ["intellect"],
        "Psyche": ["psyche"],
        "Physique": ["fysique"],
        "Motorics": ["motorics"],
        "common_ancestor": ["characterSheet"],
        "map": ["value", "valueWithoutPerceptionsSubSkills", "maximumValue"],
    },
    "char_sheet_ability_modifiers": {
        "Intellect": ["INT", 0, "amount"],
        "Psyche": ["PSY", 0, "amount"],
        "Physique": ["FYS", 0, "amount"],
        "Motorics": ["MOT", 0, "amount"],
        "common_ancestor": ["characterSheet", "AbilityModifierCauseMap"],
    },
    "Inventory": {
        "gained_items": ["gainedItems"],
        "common_ancestor": ["playerCharacter"],
    },
}


def get_from_dict(dict: dict, map: list):
    return reduce(operator.getitem, map, dict)


def get_from_dict_safe(dict: dict, map: list, default=None):
    """Safely get value from nested dict, returning default if key doesn't exist"""
    try:
        return reduce(operator.getitem, map, dict)
    except (KeyError, TypeError):
        return default


def set_in_dict(dict: dict, map: list, value):
    """Set value in nested dict, creating intermediate dicts if needed"""
    # Navigate to parent, creating dicts as needed
    current = dict
    for key in map[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    # Set the final value
    current[map[-1]] = value


class SaveState:
    def __init__(self, path):
        self._save_path = path
        self._tmp_dir = unzip_save(self._save_path)
        self._backup_path = backup_save(self._save_path)
        self._save_state_path, self._save_state = get_save_state(self._tmp_dir)

    def set_door(self, key: str, value: bool = True):
        map = MAPS["Doors"]["common_ancestor"] + MAPS["Doors"][key]
        set_in_dict(self._save_state, map, value)

    def get_door(self, key: str) -> bool:
        map = MAPS["Doors"]["common_ancestor"] + MAPS["Doors"][key]
        # Return False if door doesn't exist yet (not encountered in game)
        return get_from_dict_safe(self._save_state, map, default=False)

    def set_time(self, key: str = "Minutes Passed in Day", value: str = "04:20"):
        hours, minutes = value.split(":")
        total_minutes = 60 * int(hours) + int(minutes)
        map = MAPS["Time"]["common_ancestor"] + MAPS["Time"][key]
        set_in_dict(self._save_state, map, total_minutes)

    def get_time(self, key: str = "Minutes Passed in Day") -> str:
        map = MAPS["Time"]["common_ancestor"] + MAPS["Time"][key]
        total_minutes = get_from_dict_safe(self._save_state, map, default=0)
        hours, minutes = total_minutes // 60, total_minutes % 60
        return f"{hours}:{minutes}"

    def set_resource(self, key: str, value: int = 99):
        if key == "Money":
            value = int(value * 100)
        map = MAPS["Resources"]["common_ancestor"] + MAPS["Resources"][key]
        set_in_dict(self._save_state, map, value)

    def get_resource(self, key: str) -> int:
        map = MAPS["Resources"]["common_ancestor"] + MAPS["Resources"][key]
        return get_from_dict_safe(self._save_state, map, default=0)

    def set_all_unknown_and_forgotten_thoughts(self):
        map_root = MAPS["All Thoughts"]["map"]
        thoughts_list = get_from_dict_safe(self._save_state, map_root, default=[])
        if not thoughts_list:
            return  # No thoughts to process
        for thought in thoughts_list:
            if thought.get("state") in [
                MAPS["All Thoughts"]["forgotten_state"],
                MAPS["All Thoughts"]["unknown_state"],
            ]:
                thought["state"] = MAPS["All Thoughts"]["known_state"]
        set_in_dict(self._save_state, map_root, thoughts_list)
        # Only clear forgotten thoughts if characterSheet exists
        if "characterSheet" in self._save_state:
            self._save_state["characterSheet"]["forgottenThoughts"] = []

    def get_char_sheet_stat(self, key: str) -> int:
        map = (
            MAPS["Character Sheet"]["common_ancestor"]
            + MAPS["Character Sheet"][key]
            + [MAPS["Character Sheet"]["map"][0]]
        )
        return get_from_dict_safe(self._save_state, map, default=1)

    def set_char_sheet_stat(self, key: str, value: int):
        map = MAPS["Character Sheet"]["common_ancestor"] + MAPS["Character Sheet"][key]
        stat = get_from_dict_safe(self._save_state, map, default={})
        # If stat doesn't exist, create it with all required fields
        if not stat:
            stat = {field: value for field in MAPS["Character Sheet"]["map"]}
        else:
            for edit in MAPS["Character Sheet"]["map"]:
                stat[edit] = value
        set_in_dict(self._save_state, map, stat)
        map = (
            MAPS["char_sheet_ability_modifiers"]["common_ancestor"]
            + MAPS["char_sheet_ability_modifiers"][key]
        )
        set_in_dict(self._save_state, map, value)

    def get_inventory(self) -> list:
        """Returns list of item IDs in gainedItems"""
        map = MAPS["Inventory"]["common_ancestor"] + MAPS["Inventory"]["gained_items"]
        return get_from_dict_safe(self._save_state, map, default=[])

    def add_inventory_item(self, item_id: str) -> bool:
        """Adds item to gainedItems if not already present. Returns True if added."""
        map = MAPS["Inventory"]["common_ancestor"] + MAPS["Inventory"]["gained_items"]
        items = get_from_dict_safe(self._save_state, map, default=[])
        if item_id not in items:
            items.append(item_id)
            set_in_dict(self._save_state, map, items)
            return True
        return False

    def remove_inventory_item(self, item_id: str) -> bool:
        """Removes item from gainedItems. Returns True if removed."""
        map = MAPS["Inventory"]["common_ancestor"] + MAPS["Inventory"]["gained_items"]
        items = get_from_dict_safe(self._save_state, map, default=[])
        if item_id in items:
            items.remove(item_id)
            set_in_dict(self._save_state, map, items)
            return True
        return False

    def commit(self, **kwargs):
        write_save_state(self._save_state, self._save_state_path)
        zip_save(self._save_path, **kwargs)

    def rollback(self):
        shutil.rmtree(self._tmp_dir)
        restore_save(self._backup_path)
