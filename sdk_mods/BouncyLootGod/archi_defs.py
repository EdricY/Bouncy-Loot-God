import json
from pathlib import Path
from BouncyLootGod.archi_data import archi_data

# TODO rename this file for easier navigation

# could switch to json and use open_in_mod_dir (from mods_base)

loc_name_to_id = archi_data["loc"]
item_name_to_id = archi_data["item"]
loc_id_to_name = {id: name for name, id in loc_name_to_id.items()}
item_id_to_name = {id: name for name, id in item_name_to_id.items()}


legacy_gear_kind_to_id = { # TODO: hopefully can remove this later
    # Gear [100 - 199]
    "Common Shield":                    100,
    "Uncommon Shield":                  101,
    "Rare Shield":                      102,
    "VeryRare Shield":                  103,
    # "E-Tech Shield":                  104,
    "Legendary Shield":                 105,
    "Seraph Shield":                    106,
    "Rainbow Shield":                   107,
    # "Pearlescent Shield":             108,
    "Unique Shield":                    109,

    "Common GrenadeMod":                110,
    "Uncommon GrenadeMod":              111,
    "Rare GrenadeMod":                  112,
    "VeryRare GrenadeMod":              113,
    # "E-Tech GrenadeMod":              114,
    "Legendary GrenadeMod":             115,
    "Seraph GrenadeMod":                116,
    "Rainbow GrenadeMod":               117,
    # "Pearlescent GrenadeMod":         118,
    "Unique GrenadeMod":                119,

    "Common ClassMod":                  120,
    "Uncommon ClassMod":                121,
    "Rare ClassMod":                    122,
    "VeryRare ClassMod":                123,
    # "E-Tech ClassMod":                124,
    "Legendary ClassMod":               125,
    # "Seraph ClassMod":                126,
    # "Rainbow ClassMod":               127,
    # "Pearlescent ClassMod":           128,
    # "Unique ClassMod":                129,

    "Common Relic":                     130,
    "Uncommon Relic":                   131,
    "Rare Relic":                       132,
    "VeryRare Relic":                   133,
    "E-Tech Relic":                     134,
    # "Legendary Relic":                135,
    "Seraph Relic":                     136,
    "Rainbow Relic":                    137,
    # "Pearlescent Relic":              138,
    "Unique Relic":                     139,

    "Common Pistol":                    140,
    "Uncommon Pistol":                  141,
    "Rare Pistol":                      142,
    "VeryRare Pistol":                  143,
    "E-Tech Pistol":                    144,
    "Legendary Pistol":                 145,
    "Seraph Pistol":                    146,
    # "Rainbow Pistol":                 147,
    "Pearlescent Pistol":               148,
    "Unique Pistol":                    149,

    "Common Shotgun":                   150,
    "Uncommon Shotgun":                 151,
    "Rare Shotgun":                     152,
    "VeryRare Shotgun":                 153,
    "E-Tech Shotgun":                   154,
    "Legendary Shotgun":                155,
    "Seraph Shotgun":                   156,
    "Rainbow Shotgun":                  157,
    "Pearlescent Shotgun":              158,
    "Unique Shotgun":                   159,

    "Common SMG":                       160,
    "Uncommon SMG":                     161,
    "Rare SMG":                         162,
    "VeryRare SMG":                     163,
    "E-Tech SMG":                       164,
    "Legendary SMG":                    165,
    "Seraph SMG":                       166,
    "Rainbow SMG":                      167,
    "Pearlescent SMG":                  168,
    "Unique SMG":                       169,

    "Common SniperRifle":               170,
    "Uncommon SniperRifle":             171,
    "Rare SniperRifle":                 172,
    "VeryRare SniperRifle":             173,
    "E-Tech SniperRifle":               174,
    "Legendary SniperRifle":            175,
    "Seraph SniperRifle":               176,
    "Rainbow SniperRifle":              177,
    "Pearlescent SniperRifle":          178,
    "Unique SniperRifle":               179,

    "Common AssaultRifle":              180,
    "Uncommon AssaultRifle":            181,
    "Rare AssaultRifle":                182,
    "VeryRare AssaultRifle":            183,
    "E-Tech AssaultRifle":              184,
    "Legendary AssaultRifle":           185,
    "Seraph AssaultRifle":              186,
    "Rainbow AssaultRifle":             187,
    "Pearlescent AssaultRifle":         188,
    "Unique AssaultRifle":              189,

    "Common RocketLauncher":            190,
    "Uncommon RocketLauncher":          191,
    "Rare RocketLauncher":              192,
    "VeryRare RocketLauncher":          193,
    "E-Tech RocketLauncher":            194,
    "Legendary RocketLauncher":         195,
    "Seraph RocketLauncher":            196,
    "Rainbow RocketLauncher":           197,
    "Pearlescent RocketLauncher":       198,
    "Unique RocketLauncher":            199,
}
