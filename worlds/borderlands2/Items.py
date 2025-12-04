from typing import Dict, NamedTuple, Optional

from BaseClasses import Item, ItemClassification
from .archi_defs import item_name_to_id

bl2_base_id: int = 2388000


class Borderlands2Item(Item):
    game = "Borderlands 2"


class Borderlands2ItemData(NamedTuple):
    code: Optional[int] = None
    type: ItemClassification = ItemClassification.filler
    description: Optional[str] = None
    name: str = ""


p_items = {"Jump", "Melee", "Crouch", "Sprint", "Gear Leveler"}
u_items = {"Vehicle Fire", "Gear Leveler", "Common Shield", "Common Pistol", "Common SMG"}

item_data_table: Dict[str, Borderlands2ItemData] = {
    name: Borderlands2ItemData(
        code=bl2_base_id + item_id,
        type=ItemClassification.progression if name in p_items
        else ItemClassification.useful if name in u_items
        else ItemClassification.filler,
        description="",
        name=name,
    )
    for name, item_id in item_name_to_id.items()
}

item_name_to_id = {name: data.code for name, data in item_data_table.items() if data.code is not None}
item_descriptions = {name: data.description for name, data in item_data_table.items() if data.code is not None}

# gear_rarities = [
#     "Common",
#     "Uncommon",
#     "Rare",
#     "VeryRare",
#     "Legendary",
#     "Seraph",
#     "Rainbow",
#     "Pearlescent",
#     "Unique",
# ]
#
# gear_kinds = [
#     "Shield",
#     "GrenadeMod",
#     "ClassMod",
#     "Relic",
#     "Pistol",
#     "Shotgun",
#     "SMG",
#     "SniperRifle",
#     "AssaultRifle",
#     "RocketLauncher",
# ]
