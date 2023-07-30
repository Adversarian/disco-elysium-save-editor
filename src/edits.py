import operator
from src.utils import *
from functools import reduce

MAPS = {
    "Doors": {
        "common_ancestor": ["variousItemsHolder", "DoorStates"],
        "Whirling Door Tequila": ["Whirling Door Tequila"],
        "Bookstore Curtains": ["Bookstore Curtains"],
        "Whirling Door Klassje": ["Whirling Door Klassje"],
        "Whirling Door Bathroom Klassje": ["Whirling Door Bathroom Klassje"],
        "Door Apartment no dialogue(bathroom)": [
            "Door Apartment no dialogue(bathroom)"
        ],
        "Door Apartment 10": ["Door Apartment 10"],
        "Door Apartment 10 Open": ["Door Apartment 10 Open"],
    },
    "Time": {
        "common_ancestor": ["sunshineClockTimeHolder", "time"],
        "Minutes Passed in Day": ["dayMinutes"],
    },
    "Resources": {
        "common_ancestor": ["playerCharacter"],
        "Skill Points": ["SkillPoints"],
        "Money": ["Money"],
        "Health Consumables": ["healingPools", "ENDURANCE"],
        "Morale Consumables": ["healingPools", "VOLITION"],
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
}


def get_from_dict(dict, map):
    return reduce(operator.getitem, map, dict)


def set_in_dict(dict, map, value):
    get_from_dict(dict, map[:-1])[map[-1]] = value


class SaveState:
    def __init__(self, path):
        self._save_path = path
        self._tmp_dir = unzip_save(self._save_path)
        self._backup_path = backup_save(self._save_path)
        self._save_state_path, self._save_state = get_save_state(self._tmp_dir)

    def set_door(self, key, value=True):
        map = MAPS["Doors"]["common_ancestor"] + MAPS["Doors"][key]
        set_in_dict(self._save_state, map, value)

    def set_time(self, key="Minutes Passed in Day", value="04:20"):
        hours, minutes = value.split(":")
        total_minutes = 60 * int(hours) + int(minutes)
        map = MAPS["Time"]["common_ancestor"] + MAPS["Time"][key]
        set_in_dict(self._save_state, map, total_minutes)

    def set_resource(self, key, value=99):
        if key == "Money":
            value = int(value * 100)
        map = MAPS["Resources"]["common_ancestor"] + MAPS["Resources"][key]
        set_in_dict(self._save_state, map, value)

    def set_all_unknown_thoughts(self):
        map_root = MAPS["All Thoughts"]["map"]
        thoughts_list = get_from_dict(self._save_state, map_root)
        for thought in thoughts_list:
            if thought["state"] in [
                MAPS["All Thoughts"]["forgotten_state"],
                MAPS["All Thoughts"]["unknown_state"],
            ]:
                thought["state"] = MAPS["All Thoughts"]["known_state"]
        set_in_dict(self._save_state, map_root, thoughts_list)

    def commit(self, **kwargs):
        write_save_state(self._save_state, self._save_state_path)
        zip_save(self._save_path, **kwargs)

    def rollback(self):
        shutil.rmtree(self._tmp_dir)
        restore_save(self._backup_path)
