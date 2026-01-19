import json
from pathlib import Path
from BouncyLootGod.archi_data import archi_data

# TODO rename this file for easier navigation

# could switch to json and use open_in_mod_dir (from mods_base)

loc_name_to_id = archi_data["loc"]
item_name_to_id = archi_data["item"]
loc_id_to_name = {id: name for name, id in loc_name_to_id.items()}
item_id_to_name = {id: name for name, id in item_name_to_id.items()}


gear_kinds = {
    "Common Shield",
    "Uncommon Shield",
    "Rare Shield",
    "VeryRare Shield",
    # "E-Tech Shield",
    "Legendary Shield",
    "Seraph Shield",
    "Rainbow Shield",
    # "Pearlescent Shield",
    "Unique Shield",

    "Common GrenadeMod",
    "Uncommon GrenadeMod",
    "Rare GrenadeMod",
    "VeryRare GrenadeMod",
    # "E-Tech GrenadeMod",
    "Legendary GrenadeMod",
    "Seraph GrenadeMod",
    "Rainbow GrenadeMod",
    # "Pearlescent GrenadeMod",
    "Unique GrenadeMod",

    "Common ClassMod",
    "Uncommon ClassMod",
    "Rare ClassMod",
    "VeryRare ClassMod",
    # "E-Tech ClassMod",
    "Legendary ClassMod",
    # "Seraph ClassMod",
    # "Rainbow ClassMod",
    # "Pearlescent ClassMod",
    # "Unique ClassMod",

    "Common Relic",
    "Uncommon Relic",
    "Rare Relic",
    "VeryRare Relic",
    "E-Tech Relic",
    # "Legendary Relic",
    "Seraph Relic",
    "Rainbow Relic",
    # "Pearlescent Relic",
    "Unique Relic",

    "Common Pistol",
    "Uncommon Pistol",
    "Rare Pistol",
    "VeryRare Pistol",
    "E-Tech Pistol",
    "Legendary Pistol",
    "Seraph Pistol",
    # "Rainbow Pistol",
    "Pearlescent Pistol",
    "Unique Pistol",

    "Common Shotgun",
    "Uncommon Shotgun",
    "Rare Shotgun",
    "VeryRare Shotgun",
    "E-Tech Shotgun",
    "Legendary Shotgun",
    "Seraph Shotgun",
    "Rainbow Shotgun",
    "Pearlescent Shotgun",
    "Unique Shotgun",

    "Common SMG",
    "Uncommon SMG",
    "Rare SMG",
    "VeryRare SMG",
    "E-Tech SMG",
    "Legendary SMG",
    "Seraph SMG",
    "Rainbow SMG",
    "Pearlescent SMG",
    "Unique SMG",

    "Common SniperRifle",
    "Uncommon SniperRifle",
    "Rare SniperRifle",
    "VeryRare SniperRifle",
    "E-Tech SniperRifle",
    "Legendary SniperRifle",
    "Seraph SniperRifle",
    "Rainbow SniperRifle",
    "Pearlescent SniperRifle",
    "Unique SniperRifle",

    "Common AssaultRifle",
    "Uncommon AssaultRifle",
    "Rare AssaultRifle",
    "VeryRare AssaultRifle",
    "E-Tech AssaultRifle",
    "Legendary AssaultRifle",
    "Seraph AssaultRifle",
    "Rainbow AssaultRifle",
    "Pearlescent AssaultRifle",
    "Unique AssaultRifle",

    "Common RocketLauncher",
    "Uncommon RocketLauncher",
    "Rare RocketLauncher",
    "VeryRare RocketLauncher",
    "E-Tech RocketLauncher",
    "Legendary RocketLauncher",
    "Seraph RocketLauncher",
    "Rainbow RocketLauncher",
    "Pearlescent RocketLauncher",
    "Unique RocketLauncher",
}
