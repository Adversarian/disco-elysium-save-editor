import operator
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
