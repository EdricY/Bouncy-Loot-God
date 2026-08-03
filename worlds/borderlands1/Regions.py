from typing import Dict, List, NamedTuple, Union


class Borderlands1RegionData(NamedTuple):
    name: str = ""
    min_level: int = 0 # the lowest level you could begin farming exp in this area
    max_level: int = 0 # the highest expected level you could farm exp in this area up to
    travel_item_name: str = ""
    connecting_regions: List[str] = []
    story_req_regions: List[str] = []
    dlc_group: str = "basegame"

region_data_table: Dict[str, Borderlands1RegionData] = {
    "Menu": Borderlands1RegionData("Menu", 0, 0, "", [
        "Arid Badlands",
    ], dlc_group="menu"),

    "Arid Badlands": Borderlands1RegionData("Arid Badlands", 0, 3, "", []),
    "Skag Gully": Borderlands1RegionData("Skag Gully", 0, 3, "Travel: Skag Gully", []),
    "Arid Hills": Borderlands1RegionData("Arid Hills", 0, 3, "Travel: Arid Hills", []),
    "Sledge's Safe House": Borderlands1RegionData("Sledge's Safe House", 0, 3, "Travel: Sledge's Safe House", []),
    "The Lost Cave": Borderlands1RegionData("The Lost Cave", 0, 3, "Travel: The Lost Cave", []),
    "Headstone Mine": Borderlands1RegionData("Headstone Mine", 0, 3, "Travel: Headstone Mine", []),
    "The Dahl Headland": Borderlands1RegionData("The Dahl Headland", 0, 3, "Travel: The Dahl Headland", []),
    "Tetanus Warrens": Borderlands1RegionData("Tetanus Warrens", 0, 3, "Travel: Tetanus Warrens", []),
    "Rust Commons West": Borderlands1RegionData("Rust Commons West", 0, 3, "Travel: Rust Commons West", []),
    "Crazy Earl's Scrapyard": Borderlands1RegionData("Crazy Earl's Scrapyard", 0, 3, "Travel: Crazy Earl's Scrapyard", []),
    "Treacher's Landing": Borderlands1RegionData("Treacher's Landing", 0, 3, "Travel: Treacher's Landing", []),
    "Rust Commons East": Borderlands1RegionData("Rust Commons East", 0, 3, "Travel: Rust Commons East", []),
    "Krom's Canyon": Borderlands1RegionData("Krom's Canyon", 0, 3, "Travel: Krom's Canyon", []),
    "Trash Coast": Borderlands1RegionData("Trash Coast", 0, 3, "Travel: Trash Coast", []),
    "Old Haven": Borderlands1RegionData("Old Haven", 0, 3, "Travel: Old Haven", []),
    "Salt Flats": Borderlands1RegionData("Salt Flats", 0, 3, "Travel: Salt Flats", []),
    "The Backdoor": Borderlands1RegionData("The Backdoor", 0, 3, "Travel: The Backdoor", []),
    "Crimson Fastness": Borderlands1RegionData("Crimson Fastness", 0, 3, "Travel: Crimson Fastness", []),
    "Crimson Enclave": Borderlands1RegionData("Crimson Enclave", 0, 3, "Travel: Crimson Enclave", []),
    "The Descent": Borderlands1RegionData("The Descent", 0, 3, "Travel: The Descent", []),
    "Eridian Promontory": Borderlands1RegionData("Eridian Promontory", 0, 3, "Travel: Eridian Promontory", []),
    "The Vault": Borderlands1RegionData("The Vault", 0, 3, "Travel: The Vault", []),

    "Jakobs Cove": Borderlands1RegionData("Jakobs Cove", 0, 3, "Travel: Jakobs Cove", [], dlc_group="ned"),
    "Generally Hospital": Borderlands1RegionData("Generally Hospital", 0, 3, "Travel: Generally Hospital", [], dlc_group="ned"),
    "The Lumber Yard": Borderlands1RegionData("The Lumber Yard", 0, 3, "Travel: The Lumber Yard", [], dlc_group="ned"),
    "Hollow's End": Borderlands1RegionData("Hollow's End", 0, 3, "Travel: Hollow's End", [], dlc_group="ned"),
    "Dead Haven": Borderlands1RegionData("Dead Haven", 0, 3, "Travel: Dead Haven", [], dlc_group="ned"),
    "The Mill": Borderlands1RegionData("The Mill", 0, 3, "Travel: The Mill", [], dlc_group="ned"),

    "The Underdome": Borderlands1RegionData("The Underdome", 0, 3, "Travel: The Underdome", [], dlc_group="moxxi"),
    "Hell-Burbia": Borderlands1RegionData("Hell-Burbia", 0, 3, "Travel: Hell-Burbia", [], dlc_group="moxxi"),
    "The Angelic Ruins": Borderlands1RegionData("The Angelic Ruins", 0, 3, "Travel: The Angelic Ruins", [], dlc_group="moxxi"),
    "The Gully": Borderlands1RegionData("The Gully", 0, 3, "Travel: The Gully", [], dlc_group="moxxi"),

    "T-Bone Junction": Borderlands1RegionData("T-Bone Junction", 0, 3, "Travel: T-Bone Junction", [], dlc_group="knoxx"),
    "The Crimson Tollway": Borderlands1RegionData("The Crimson Tollway", 0, 3, "Travel: The Crimson Tollway", [], dlc_group="knoxx"),
    "The Ridgeway": Borderlands1RegionData("The Ridgeway", 0, 3, "Travel: The Ridgeway", [], dlc_group="knoxx"),
    "Sunken Sea": Borderlands1RegionData("Sunken Sea", 0, 3, "Travel: Sunken Sea", [], dlc_group="knoxx"),
    "Lockdown Palace": Borderlands1RegionData("Lockdown Palace", 0, 3, "Travel: Lockdown Palace", [], dlc_group="knoxx"),
    "Circle of Duty": Borderlands1RegionData("Circle of Duty", 0, 3, "Travel: Circle of Duty", [], dlc_group="knoxx"),
    "Road's End": Borderlands1RegionData("Road's End", 0, 3, "Travel: Road's End", [], dlc_group="knoxx"),
    "Deep Fathom": Borderlands1RegionData("Deep Fathom", 0, 3, "Travel: Deep Fathom", [], dlc_group="knoxx"),
    "Crimson Armory": Borderlands1RegionData("Crimson Armory", 0, 3, "Travel: Crimson Armory", [], dlc_group="knoxx"),

    "Tartarus Station": Borderlands1RegionData("Tartarus Station", 0, 3, "Travel: Tartarus Station", [], dlc_group="claptrap"),
    "Hyperion Dump": Borderlands1RegionData("Hyperion Dump", 0, 3, "Travel: Hyperion Dump", [], dlc_group="claptrap"),
    "Sanders Gorge": Borderlands1RegionData("Sanders Gorge", 0, 3, "Travel: Sanders Gorge", [], dlc_group="claptrap"),
    "Dividing Faults": Borderlands1RegionData("Dividing Faults", 0, 3, "Travel: Dividing Faults", [], dlc_group="claptrap"),
    "Scorched Snake Canyon": Borderlands1RegionData("Scorched Snake Canyon", 0, 3, "Travel: Scorched Snake Canyon", [], dlc_group="claptrap"),
    "Wayward Pass": Borderlands1RegionData("Wayward Pass", 0, 3, "Travel: Wayward Pass", [], dlc_group="claptrap"),
    "Marcus' Mission": Borderlands1RegionData("Marcus' Mission", 0, 3, "Travel: Marcus' Mission", [], dlc_group="claptrap"),
}

progressive_travel_dict = {
    "basegame": [r for r in region_data_table if region_data_table[r].dlc_group == "basegame"],
    "basegame_side": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "basegame_side"],
    "ned": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "ned"],
    "moxxi": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "moxxi"],
    "knoxx": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "knoxx"],
    "claptrap": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "claptrap"],
}

progressive_travel_items = {
    "basegame": "Progressive Travel: Base Game",
    "basegame_side": "Progressive Travel: Base Game",
    "ned": "Progressive Travel: Ned DLC",
    "moxxi": "Progressive Travel: Moxxi DLC",
    "knoxx": "Progressive Travel: Knoxx DLC",
    "claptrap": "Progressive Travel: Claptrap DLC",
}
