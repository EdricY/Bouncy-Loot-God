from typing import Dict, NamedTuple, Optional

from BaseClasses import Item, ItemClassification

bl2_base_id: int = 2388000


class Borderlands2Item(Item):
    game = "Borderlands 2"


class Borderlands2ItemData(NamedTuple):
    code: Optional[int] = None
    type: ItemClassification = ItemClassification.filler
    description: Optional[str] = None


item_rarities = [
    "Common",
    "Uncommon",
    "Rare",
    "VeryRare",
    "Legendary",
    "Seraph",
    "Rainbow",
    "Pearlescent",
    "Unique",
]

item_kinds = [
    "Shield",
    "GrenadeMod",
    "ClassMod",
    "Relic",
    "Pistol",
    "Shotgun",
    "SMG",
    "SniperRifle",
    "AssaultRifle",
    "RocketLauncher",
]

item_data_table: Dict[str, Borderlands2ItemData] = {
    "Common Shield":                Borderlands2ItemData(code=bl2_base_id +  1, type=ItemClassification.progression, description=""),
    "Uncommon Shield":              Borderlands2ItemData(code=bl2_base_id +  2, type=ItemClassification.progression, description=""),
    "Rare Shield":                  Borderlands2ItemData(code=bl2_base_id +  3, type=ItemClassification.progression, description=""),
    "VeryRare Shield":              Borderlands2ItemData(code=bl2_base_id +  4, type=ItemClassification.progression, description=""),
    "Legendary Shield":             Borderlands2ItemData(code=bl2_base_id +  5, type=ItemClassification.progression, description=""),
    # "Seraph Shield":                Borderlands2ItemData(code=bl2_base_id +  6, type=ItemClassification.progression, description=""),
    # "Rainbow Shield":               Borderlands2ItemData(code=bl2_base_id +  7, type=ItemClassification.progression, description=""),
    # "Pearlescent Shield":           Borderlands2ItemData(code=bl2_base_id +  8, type=ItemClassification.progression, description=""),
    "Unique Shield":                Borderlands2ItemData(code=bl2_base_id +  9, type=ItemClassification.progression, description=""),

    "Common GrenadeMod":            Borderlands2ItemData(code=bl2_base_id + 10, type=ItemClassification.progression, description=""),
    "Uncommon GrenadeMod":          Borderlands2ItemData(code=bl2_base_id + 11, type=ItemClassification.progression, description=""),
    "Rare GrenadeMod":              Borderlands2ItemData(code=bl2_base_id + 12, type=ItemClassification.progression, description=""),
    "VeryRare GrenadeMod":          Borderlands2ItemData(code=bl2_base_id + 13, type=ItemClassification.progression, description=""),
    "Legendary GrenadeMod":         Borderlands2ItemData(code=bl2_base_id + 14, type=ItemClassification.progression, description=""),
    # "Seraph GrenadeMod":            Borderlands2ItemData(code=bl2_base_id + 15, type=ItemClassification.progression, description=""),
    # "Rainbow GrenadeMod":           Borderlands2ItemData(code=bl2_base_id + 16, type=ItemClassification.progression, description=""),
    # "Pearlescent GrenadeMod":       Borderlands2ItemData(code=bl2_base_id + 17, type=ItemClassification.progression, description=""),
    "Unique GrenadeMod":            Borderlands2ItemData(code=bl2_base_id + 18, type=ItemClassification.progression, description=""),

    "Common ClassMod":              Borderlands2ItemData(code=bl2_base_id + 19, type=ItemClassification.progression, description=""),
    "Uncommon ClassMod":            Borderlands2ItemData(code=bl2_base_id + 20, type=ItemClassification.progression, description=""),
    "Rare ClassMod":                Borderlands2ItemData(code=bl2_base_id + 21, type=ItemClassification.progression, description=""),
    "VeryRare ClassMod":            Borderlands2ItemData(code=bl2_base_id + 22, type=ItemClassification.progression, description=""),
    "Legendary ClassMod":           Borderlands2ItemData(code=bl2_base_id + 23, type=ItemClassification.progression, description=""),
    # "Seraph ClassMod":              Borderlands2ItemData(code=bl2_base_id + 24, type=ItemClassification.progression, description=""),
    # "Rainbow ClassMod":             Borderlands2ItemData(code=bl2_base_id + 25, type=ItemClassification.progression, description=""),
    # "Pearlescent ClassMod":         Borderlands2ItemData(code=bl2_base_id + 26, type=ItemClassification.progression, description=""),
    "Unique ClassMod":              Borderlands2ItemData(code=bl2_base_id + 27, type=ItemClassification.progression, description=""),

    "Common Relic":                 Borderlands2ItemData(code=bl2_base_id + 28, type=ItemClassification.progression, description=""),
    "Uncommon Relic":               Borderlands2ItemData(code=bl2_base_id + 29, type=ItemClassification.progression, description=""),
    "Rare Relic":                   Borderlands2ItemData(code=bl2_base_id + 30, type=ItemClassification.progression, description=""),
    "VeryRare Relic":               Borderlands2ItemData(code=bl2_base_id + 31, type=ItemClassification.progression, description=""),
    "Legendary Relic":              Borderlands2ItemData(code=bl2_base_id + 32, type=ItemClassification.progression, description=""),
    # "Seraph Relic":                 Borderlands2ItemData(code=bl2_base_id + 33, type=ItemClassification.progression, description=""),
    # "Rainbow Relic":                Borderlands2ItemData(code=bl2_base_id + 34, type=ItemClassification.progression, description=""),
    # "Pearlescent Relic":            Borderlands2ItemData(code=bl2_base_id + 35, type=ItemClassification.progression, description=""),
    "Unique Relic":                 Borderlands2ItemData(code=bl2_base_id + 36, type=ItemClassification.progression, description=""),

    "Common Pistol":                Borderlands2ItemData(code=bl2_base_id + 37, type=ItemClassification.progression, description=""),
    "Uncommon Pistol":              Borderlands2ItemData(code=bl2_base_id + 38, type=ItemClassification.progression, description=""),
    "Rare Pistol":                  Borderlands2ItemData(code=bl2_base_id + 39, type=ItemClassification.progression, description=""),
    "VeryRare Pistol":              Borderlands2ItemData(code=bl2_base_id + 40, type=ItemClassification.progression, description=""),
    "Legendary Pistol":             Borderlands2ItemData(code=bl2_base_id + 41, type=ItemClassification.progression, description=""),
    # "Seraph Pistol":                Borderlands2ItemData(code=bl2_base_id + 42, type=ItemClassification.progression, description=""),
    # "Rainbow Pistol":               Borderlands2ItemData(code=bl2_base_id + 43, type=ItemClassification.progression, description=""),
    # "Pearlescent Pistol":           Borderlands2ItemData(code=bl2_base_id + 44, type=ItemClassification.progression, description=""),
    "Unique Pistol":                Borderlands2ItemData(code=bl2_base_id + 45, type=ItemClassification.progression, description=""),

    "Common Shotgun":               Borderlands2ItemData(code=bl2_base_id + 46, type=ItemClassification.progression, description=""),
    "Uncommon Shotgun":             Borderlands2ItemData(code=bl2_base_id + 47, type=ItemClassification.progression, description=""),
    "Rare Shotgun":                 Borderlands2ItemData(code=bl2_base_id + 48, type=ItemClassification.progression, description=""),
    "VeryRare Shotgun":             Borderlands2ItemData(code=bl2_base_id + 49, type=ItemClassification.progression, description=""),
    "Legendary Shotgun":            Borderlands2ItemData(code=bl2_base_id + 50, type=ItemClassification.progression, description=""),
    # "Seraph Shotgun":               Borderlands2ItemData(code=bl2_base_id + 51, type=ItemClassification.progression, description=""),
    # "Rainbow Shotgun":              Borderlands2ItemData(code=bl2_base_id + 52, type=ItemClassification.progression, description=""),
    # "Pearlescent Shotgun":          Borderlands2ItemData(code=bl2_base_id + 53, type=ItemClassification.progression, description=""),
    "Unique Shotgun":               Borderlands2ItemData(code=bl2_base_id + 54, type=ItemClassification.progression, description=""),

    "Common SMG":                   Borderlands2ItemData(code=bl2_base_id + 55, type=ItemClassification.progression, description=""),
    "Uncommon SMG":                 Borderlands2ItemData(code=bl2_base_id + 56, type=ItemClassification.progression, description=""),
    "Rare SMG":                     Borderlands2ItemData(code=bl2_base_id + 57, type=ItemClassification.progression, description=""),
    "VeryRare SMG":                 Borderlands2ItemData(code=bl2_base_id + 58, type=ItemClassification.progression, description=""),
    "Legendary SMG":                Borderlands2ItemData(code=bl2_base_id + 59, type=ItemClassification.progression, description=""),
    # "Seraph SMG":                   Borderlands2ItemData(code=bl2_base_id + 60, type=ItemClassification.progression, description=""),
    # "Rainbow SMG":                  Borderlands2ItemData(code=bl2_base_id + 61, type=ItemClassification.progression, description=""),
    # "Pearlescent SMG":              Borderlands2ItemData(code=bl2_base_id + 62, type=ItemClassification.progression, description=""),
    "Unique SMG":                   Borderlands2ItemData(code=bl2_base_id + 63, type=ItemClassification.progression, description=""),

    "Common SniperRifle":           Borderlands2ItemData(code=bl2_base_id + 64, type=ItemClassification.progression, description=""),
    "Uncommon SniperRifle":         Borderlands2ItemData(code=bl2_base_id + 65, type=ItemClassification.progression, description=""),
    "Rare SniperRifle":             Borderlands2ItemData(code=bl2_base_id + 66, type=ItemClassification.progression, description=""),
    "VeryRare SniperRifle":         Borderlands2ItemData(code=bl2_base_id + 67, type=ItemClassification.progression, description=""),
    "Legendary SniperRifle":        Borderlands2ItemData(code=bl2_base_id + 68, type=ItemClassification.progression, description=""),
    # "Seraph SniperRifle":           Borderlands2ItemData(code=bl2_base_id + 69, type=ItemClassification.progression, description=""),
    # "Rainbow SniperRifle":          Borderlands2ItemData(code=bl2_base_id + 70, type=ItemClassification.progression, description=""),
    # "Pearlescent SniperRifle":      Borderlands2ItemData(code=bl2_base_id + 71, type=ItemClassification.progression, description=""),
    "Unique SniperRifle":           Borderlands2ItemData(code=bl2_base_id + 72, type=ItemClassification.progression, description=""),

    "Common AssaultRifle":          Borderlands2ItemData(code=bl2_base_id + 73, type=ItemClassification.progression, description=""),
    "Uncommon AssaultRifle":        Borderlands2ItemData(code=bl2_base_id + 74, type=ItemClassification.progression, description=""),
    "Rare AssaultRifle":            Borderlands2ItemData(code=bl2_base_id + 75, type=ItemClassification.progression, description=""),
    "VeryRare AssaultRifle":        Borderlands2ItemData(code=bl2_base_id + 76, type=ItemClassification.progression, description=""),
    "Legendary AssaultRifle":       Borderlands2ItemData(code=bl2_base_id + 77, type=ItemClassification.progression, description=""),
    # "Seraph AssaultRifle":          Borderlands2ItemData(code=bl2_base_id + 78, type=ItemClassification.progression, description=""),
    # "Rainbow AssaultRifle":         Borderlands2ItemData(code=bl2_base_id + 79, type=ItemClassification.progression, description=""),
    # "Pearlescent AssaultRifle":     Borderlands2ItemData(code=bl2_base_id + 80, type=ItemClassification.progression, description=""),
    "Unique AssaultRifle":          Borderlands2ItemData(code=bl2_base_id + 81, type=ItemClassification.progression, description=""),

    "Common RocketLauncher":        Borderlands2ItemData(code=bl2_base_id + 82, type=ItemClassification.progression, description=""),
    "Uncommon RocketLauncher":      Borderlands2ItemData(code=bl2_base_id + 83, type=ItemClassification.progression, description=""),
    "Rare RocketLauncher":          Borderlands2ItemData(code=bl2_base_id + 84, type=ItemClassification.progression, description=""),
    "VeryRare RocketLauncher":      Borderlands2ItemData(code=bl2_base_id + 85, type=ItemClassification.progression, description=""),
    "Legendary RocketLauncher":     Borderlands2ItemData(code=bl2_base_id + 86, type=ItemClassification.progression, description=""),
    # "Seraph RocketLauncher":        Borderlands2ItemData(code=bl2_base_id + 87, type=ItemClassification.progression, description=""),
    # "Rainbow RocketLauncher":       Borderlands2ItemData(code=bl2_base_id + 88, type=ItemClassification.progression, description=""),
    # "Pearlescent RocketLauncher":   Borderlands2ItemData(code=bl2_base_id + 89, type=ItemClassification.progression, description=""),
    "Unique RocketLauncher":        Borderlands2ItemData(code=bl2_base_id + 90, type=ItemClassification.progression, description=""),
}

item_name_to_id = {name: data.code for name, data in item_data_table.items() if data.code is not None}
item_descriptions = {name: data.description for name, data in item_data_table.items() if data.code is not None}
