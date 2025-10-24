from typing import Dict, NamedTuple, Optional

from BaseClasses import Location

bl2_base_id: int = 2388000


class Borderlands2Location(Location):
    game = "Borderlands 2"


class Borderlands2LocationData(NamedTuple):
    region: str
    address: Optional[int] = None
    description: Optional[str] = None


location_data_table: Dict[str, Borderlands2LocationData] = {
    "Common Shield": Borderlands2LocationData(region="Menu", address=bl2_base_id + 1, description=""),
    "Uncommon Shield": Borderlands2LocationData(region="Menu", address=bl2_base_id + 2, description=""),
    "Rare Shield": Borderlands2LocationData(region="Menu", address=bl2_base_id + 3, description=""),
    "VeryRare Shield": Borderlands2LocationData(region="Menu", address=bl2_base_id + 4, description=""),
    "Legendary Shield": Borderlands2LocationData(region="Menu", address=bl2_base_id + 5, description=""),
    # "Seraph Shield": Borderlands2LocationData(region="Menu", address=bl2_base_id + 6, description=""),
    # "Rainbow Shield": Borderlands2LocationData(region="Menu", address=bl2_base_id + 7, description=""),
    # "Pearlescent Shield": Borderlands2LocationData(region="Menu", address=bl2_base_id + 8, description=""),
    "Unique Shield": Borderlands2LocationData(region="Menu", address=bl2_base_id + 9, description=""),

    "Common GrenadeMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 10, description=""),
    "Uncommon GrenadeMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 11, description=""),
    "Rare GrenadeMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 12, description=""),
    "VeryRare GrenadeMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 13, description=""),
    "Legendary GrenadeMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 14, description=""),
    # "Seraph GrenadeMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 15, description=""),
    # "Rainbow GrenadeMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 16, description=""),
    # "Pearlescent GrenadeMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 17, description=""),
    "Unique GrenadeMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 18, description=""),

    "Common ClassMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 19, description=""),
    "Uncommon ClassMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 20, description=""),
    "Rare ClassMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 21, description=""),
    "VeryRare ClassMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 22, description=""),
    "Legendary ClassMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 23, description=""),
    # "Seraph ClassMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 24, description=""),
    # "Rainbow ClassMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 25, description=""),
    # "Pearlescent ClassMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 26, description=""),
    "Unique ClassMod": Borderlands2LocationData(region="Menu", address=bl2_base_id + 27, description=""),

    "Common Relic": Borderlands2LocationData(region="Menu", address=bl2_base_id + 28, description=""),
    "Uncommon Relic": Borderlands2LocationData(region="Menu", address=bl2_base_id + 29, description=""),
    "Rare Relic": Borderlands2LocationData(region="Menu", address=bl2_base_id + 30, description=""),
    "VeryRare Relic": Borderlands2LocationData(region="Menu", address=bl2_base_id + 31, description=""),
    "Legendary Relic": Borderlands2LocationData(region="Menu", address=bl2_base_id + 32, description=""),
    # "Seraph Relic": Borderlands2LocationData(region="Menu", address=bl2_base_id + 33, description=""),
    # "Rainbow Relic": Borderlands2LocationData(region="Menu", address=bl2_base_id + 34, description=""),
    # "Pearlescent Relic": Borderlands2LocationData(region="Menu", address=bl2_base_id + 35, description=""),
    "Unique Relic": Borderlands2LocationData(region="Menu", address=bl2_base_id + 36, description=""),

    "Common Pistol": Borderlands2LocationData(region="Menu", address=bl2_base_id + 37, description=""),
    "Uncommon Pistol": Borderlands2LocationData(region="Menu", address=bl2_base_id + 38, description=""),
    "Rare Pistol": Borderlands2LocationData(region="Menu", address=bl2_base_id + 39, description=""),
    "VeryRare Pistol": Borderlands2LocationData(region="Menu", address=bl2_base_id + 40, description=""),
    "Legendary Pistol": Borderlands2LocationData(region="Menu", address=bl2_base_id + 41, description=""),
    # "Seraph Pistol": Borderlands2LocationData(region="Menu", address=bl2_base_id + 42, description=""),
    # "Rainbow Pistol": Borderlands2LocationData(region="Menu", address=bl2_base_id + 43, description=""),
    # "Pearlescent Pistol": Borderlands2LocationData(region="Menu", address=bl2_base_id + 44, description=""),
    "Unique Pistol": Borderlands2LocationData(region="Menu", address=bl2_base_id + 45, description=""),

    "Common Shotgun": Borderlands2LocationData(region="Menu", address=bl2_base_id + 46, description=""),
    "Uncommon Shotgun": Borderlands2LocationData(region="Menu", address=bl2_base_id + 47, description=""),
    "Rare Shotgun": Borderlands2LocationData(region="Menu", address=bl2_base_id + 48, description=""),
    "VeryRare Shotgun": Borderlands2LocationData(region="Menu", address=bl2_base_id + 49, description=""),
    "Legendary Shotgun": Borderlands2LocationData(region="Menu", address=bl2_base_id + 50, description=""),
    # "Seraph Shotgun": Borderlands2LocationData(region="Menu", address=bl2_base_id + 51, description=""),
    # "Rainbow Shotgun": Borderlands2LocationData(region="Menu", address=bl2_base_id + 52, description=""),
    # "Pearlescent Shotgun": Borderlands2LocationData(region="Menu", address=bl2_base_id + 53, description=""),
    "Unique Shotgun": Borderlands2LocationData(region="Menu", address=bl2_base_id + 54, description=""),

    "Common SMG": Borderlands2LocationData(region="Menu", address=bl2_base_id + 55, description=""),
    "Uncommon SMG": Borderlands2LocationData(region="Menu", address=bl2_base_id + 56, description=""),
    "Rare SMG": Borderlands2LocationData(region="Menu", address=bl2_base_id + 57, description=""),
    "VeryRare SMG": Borderlands2LocationData(region="Menu", address=bl2_base_id + 58, description=""),
    "Legendary SMG": Borderlands2LocationData(region="Menu", address=bl2_base_id + 59, description=""),
    # "Seraph SMG": Borderlands2LocationData(region="Menu", address=bl2_base_id + 60, description=""),
    # "Rainbow SMG": Borderlands2LocationData(region="Menu", address=bl2_base_id + 61, description=""),
    # "Pearlescent SMG": Borderlands2LocationData(region="Menu", address=bl2_base_id + 62, description=""),
    "Unique SMG": Borderlands2LocationData(region="Menu", address=bl2_base_id + 63, description=""),

    "Common SniperRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 64, description=""),
    "Uncommon SniperRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 65, description=""),
    "Rare SniperRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 66, description=""),
    "VeryRare SniperRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 67, description=""),
    "Legendary SniperRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 68, description=""),
    # "Seraph SniperRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 69, description=""),
    # "Rainbow SniperRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 70, description=""),
    # "Pearlescent SniperRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 71, description=""),
    "Unique SniperRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 72, description=""),

    "Common AssaultRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 73, description=""),
    "Uncommon AssaultRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 74, description=""),
    "Rare AssaultRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 75, description=""),
    "VeryRare AssaultRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 76, description=""),
    "Legendary AssaultRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 77, description=""),
    # "Seraph AssaultRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 78, description=""),
    # "Rainbow AssaultRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 79, description=""),
    # "Pearlescent AssaultRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 80, description=""),
    "Unique AssaultRifle": Borderlands2LocationData(region="Menu", address=bl2_base_id + 81, description=""),

    "Common RocketLauncher": Borderlands2LocationData(region="Menu", address=bl2_base_id + 82, description=""),
    "Uncommon RocketLauncher": Borderlands2LocationData(region="Menu", address=bl2_base_id + 83, description=""),
    "Rare RocketLauncher": Borderlands2LocationData(region="Menu", address=bl2_base_id + 84, description=""),
    "VeryRare RocketLauncher": Borderlands2LocationData(region="Menu", address=bl2_base_id + 85, description=""),
    "Legendary RocketLauncher": Borderlands2LocationData(region="Menu", address=bl2_base_id + 86, description=""),
    # "Seraph RocketLauncher": Borderlands2LocationData(region="Menu", address=bl2_base_id + 87, description=""),
    # "Rainbow RocketLauncher": Borderlands2LocationData(region="Menu", address=bl2_base_id + 88, description=""),
    # "Pearlescent RocketLauncher": Borderlands2LocationData(region="Menu", address=bl2_base_id + 89, description=""),
    "Unique RocketLauncher": Borderlands2LocationData(region="Menu", address=bl2_base_id + 90, description=""),
}

location_name_to_id = {name: data.address for name, data in location_data_table.items() if data.address is not None}

location_descriptions = {name: data.description for name, data in location_data_table.items() if data.address is not None}
