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
}


def get_from_dict(dict: dict, map: list):
    return reduce(operator.getitem, map, dict)


def set_in_dict(dict: dict, map: list, value):
    get_from_dict(dict, map[:-1])[map[-1]] = value


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
        return get_from_dict(self._save_state, map)

    def set_time(self, key: str = "Minutes Passed in Day", value: str = "04:20"):
        hours, minutes = value.split(":")
        total_minutes = 60 * int(hours) + int(minutes)
        map = MAPS["Time"]["common_ancestor"] + MAPS["Time"][key]
        set_in_dict(self._save_state, map, total_minutes)

    def get_time(self, key: str = "Minutes Passed in Day") -> str:
        map = MAPS["Time"]["common_ancestor"] + MAPS["Time"][key]
        total_minutes = get_from_dict(self._save_state, map)
        hours, minutes = total_minutes // 60, total_minutes % 60
        return f"{hours}:{minutes}"

    def set_resource(self, key: str, value: int = 99):
        if key == "Money":
            value = int(value * 100)
        map = MAPS["Resources"]["common_ancestor"] + MAPS["Resources"][key]
        set_in_dict(self._save_state, map, value)

    def get_resource(self, key: str) -> int:
        map = MAPS["Resources"]["common_ancestor"] + MAPS["Resources"][key]
        return get_from_dict(self._save_state, map)

    def set_all_unknown_and_forgotten_thoughts(self):
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
