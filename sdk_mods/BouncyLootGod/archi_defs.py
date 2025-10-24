bl2_base_id = 2388000
item_name_to_id = {
    "Common Shield":                    bl2_base_id +  1,
    "Uncommon Shield":                  bl2_base_id +  2,
    "Rare Shield":                      bl2_base_id +  3,
    "VeryRare Shield":                  bl2_base_id +  4,
    "Legendary Shield":                 bl2_base_id +  5,
    # "Seraph Shield":                    bl2_base_id +  6,
    # "Rainbow Shield":                   bl2_base_id +  7,
    # "Pearlescent Shield":               bl2_base_id +  8,
    "Unique Shield":                    bl2_base_id +  9,

    "Common GrenadeMod":                bl2_base_id + 10,
    "Uncommon GrenadeMod":              bl2_base_id + 11,
    "Rare GrenadeMod":                  bl2_base_id + 12,
    "VeryRare GrenadeMod":              bl2_base_id + 13,
    "Legendary GrenadeMod":             bl2_base_id + 14,
    # "Seraph GrenadeMod":                bl2_base_id + 15,
    # "Rainbow GrenadeMod":               bl2_base_id + 16,
    # "Pearlescent GrenadeMod":           bl2_base_id + 17,
    "Unique GrenadeMod":                bl2_base_id + 18,

    "Common ClassMod":                  bl2_base_id + 19,
    "Uncommon ClassMod":                bl2_base_id + 20,
    "Rare ClassMod":                    bl2_base_id + 21,
    "VeryRare ClassMod":                bl2_base_id + 22,
    "Legendary ClassMod":               bl2_base_id + 23,
    # "Seraph ClassMod":                  bl2_base_id + 24,
    # "Rainbow ClassMod":                 bl2_base_id + 25,
    # "Pearlescent ClassMod":             bl2_base_id + 26,
    "Unique ClassMod":                  bl2_base_id + 27,

    "Common Relic":                     bl2_base_id + 28,
    "Uncommon Relic":                   bl2_base_id + 29,
    "Rare Relic":                       bl2_base_id + 30,
    "VeryRare Relic":                   bl2_base_id + 31,
    "Legendary Relic":                  bl2_base_id + 32,
    # "Seraph Relic":                     bl2_base_id + 33,
    # "Rainbow Relic":                    bl2_base_id + 34,
    # "Pearlescent Relic":                bl2_base_id + 35,
    "Unique Relic":                     bl2_base_id + 36,

    "Common Pistol":                    bl2_base_id + 37,
    "Uncommon Pistol":                  bl2_base_id + 38,
    "Rare Pistol":                      bl2_base_id + 39,
    "VeryRare Pistol":                  bl2_base_id + 40,
    "Legendary Pistol":                 bl2_base_id + 41,
    # "Seraph Pistol":                    bl2_base_id + 42,
    # "Rainbow Pistol":                   bl2_base_id + 43,
    # "Pearlescent Pistol":               bl2_base_id + 44,
    "Unique Pistol":                    bl2_base_id + 45,

    "Common Shotgun":                   bl2_base_id + 46,
    "Uncommon Shotgun":                 bl2_base_id + 47,
    "Rare Shotgun":                     bl2_base_id + 48,
    "VeryRare Shotgun":                 bl2_base_id + 49,
    "Legendary Shotgun":                bl2_base_id + 50,
    # "Seraph Shotgun":                   bl2_base_id + 51,
    # "Rainbow Shotgun":                  bl2_base_id + 52,
    # "Pearlescent Shotgun":              bl2_base_id + 53,
    "Unique Shotgun":                   bl2_base_id + 54,

    "Common SMG":                       bl2_base_id + 55,
    "Uncommon SMG":                     bl2_base_id + 56,
    "Rare SMG":                         bl2_base_id + 57,
    "VeryRare SMG":                     bl2_base_id + 58,
    "Legendary SMG":                    bl2_base_id + 59,
    # "Seraph SMG":                       bl2_base_id + 60,
    # "Rainbow SMG":                      bl2_base_id + 61,
    # "Pearlescent SMG":                  bl2_base_id + 62,
    "Unique SMG":                       bl2_base_id + 63,

    "Common SniperRifle":               bl2_base_id + 64,
    "Uncommon SniperRifle":             bl2_base_id + 65,
    "Rare SniperRifle":                 bl2_base_id + 66,
    "VeryRare SniperRifle":             bl2_base_id + 67,
    "Legendary SniperRifle":            bl2_base_id + 68,
    # "Seraph SniperRifle":               bl2_base_id + 69,
    # "Rainbow SniperRifle":              bl2_base_id + 70,
    # "Pearlescent SniperRifle":          bl2_base_id + 71,
    "Unique SniperRifle":               bl2_base_id + 72,

    "Common AssaultRifle":              bl2_base_id + 73,
    "Uncommon AssaultRifle":            bl2_base_id + 74,
    "Rare AssaultRifle":                bl2_base_id + 75,
    "VeryRare AssaultRifle":            bl2_base_id + 76,
    "Legendary AssaultRifle":           bl2_base_id + 77,
    # "Seraph AssaultRifle":              bl2_base_id + 78,
    # "Rainbow AssaultRifle":             bl2_base_id + 79,
    # "Pearlescent AssaultRifle":         bl2_base_id + 80,
    "Unique AssaultRifle":              bl2_base_id + 81,

    "Common RocketLauncher":            bl2_base_id + 82,
    "Uncommon RocketLauncher":          bl2_base_id + 83,
    "Rare RocketLauncher":              bl2_base_id + 84,
    "VeryRare RocketLauncher":          bl2_base_id + 85,
    "Legendary RocketLauncher":         bl2_base_id + 86,
    # "Seraph RocketLauncher":            bl2_base_id + 87,
    # "Rainbow RocketLauncher":           bl2_base_id + 88,
    # "Pearlescent RocketLauncher":       bl2_base_id + 89,
    "Unique RocketLauncher":            bl2_base_id + 90,
}

item_id_to_name = {id: name for name, id in item_name_to_id.items()}

# def get_item_name_to_id():
#     return item_name_to_id
#     # print("from asdf file")
#     # return

# def get_item_id_to_name():
#     return item_id_to_name
