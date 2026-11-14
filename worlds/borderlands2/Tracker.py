from typing import Any

def bl2_map_tracker_index(data: Any) -> int:
    if data is None or data == "" or data == b"":
        return 0

    try: 
        if isinstance(data, str):
            data = data.strip()
            if not data:
                return 0
            internal_map_id = data
    except (ValueError, TypeError):
        return 0

    internal_map_to_tab = {
    "fyrestone_p":              36,
    "luckys_p":                 24,
    "southpawfactory_p":        13,
    "sanctuary_hole_p":         30,
    "finalbossascent_p":        38,
    "dam_p":                    15,
    "frost_p":                  12,
    "sanctuary_p":              5,
    "sanctuaryair_p":           6,
    "grass_cliffs_p":           28,
    "tundratrain_p":            19,
    "pandorapark_p":            25,
    "thresherraid_p":           40,
    "tundraexpress_p":          18,
    "fridge_p":                 20,
    "banditslaughter_p":        21,
    "cove_p":                   9,
    "icecanyon_p":              11,
    "ice_p":                    10,
    "grass_p":                  22,
    "creatureslaughter_p":      26,
    "interlude_p":              14,
    "hypinterlude_p":           17,
    "hyperioncity_p":           27,
    "damtop_p":                 16,
    "stockade_p":               37,
    "southernshelf_p":          8,
    "outwash_p":                22,
    "caverns_p":                31,
    "grass_lynchwood_p":        32,
    "glacial_p":                7,
    "craterlake_p":             35,
    "robotslaughter_p":         34,
    "boss_cliffs_p":            29,
    "vogchamber_p":             29,
    "boss_volcano_p":           39,
    "ash_p":                    33,
    "hunger_p":                 77,
    "xmas_p":                   79,
    "helios_p":                 73,
    "gaiussanctuary_p":         75,
    "backburner_p":             70,
    "sanctintro_p":             69,
    "olddust_p":                71,
    "researchcenter_p":         74,
    "sandworm_p":               72,
    "sandwormlair_p":           76,
    "dark_forest_p":            61,
    "dead_forest_p":            62,
    "castlekeep_p":             66,
    "docks_p":                  59,
    "village_p":                60,
    "castleexterior_p":         64,
    "dungeon_p":                65,
    "templeslaughter_p":        67,
    "mines_p":                  63,
    "dungeonraid_p":            68,
    "pumpkin_patch_p":          77,
    "iris_dl1_p":               49,
    "iris_dl1_tas_p":           49,
    "iris_dl2_p":               50,
    "iris_dl3_p":               53,
    "iris_hub_p":               48,
    "iris_hub2_p":              52,
    "iris_dl2_interior_p":      51,
    "iris_moxxi_p":             48,
    "testingzone_p":            82,
    "easter_p":                 81,
    "distillery_p":             80,
    "orchid_wormbelly_p":       47,
    "orchid_refinery_p":        45,
    "orchid_saltflats_p":       42,
    "orchid_spire_p":           46,
    "orchid_shipgraveyard_p":   44,
    "orchid_caves_p":           43,
    "orchid_oasistown_p":       41,
    "sage_powerstation_p":      56,
    "sage_underground_p":       54,
    "sage_cliffs_p":            57,
    "sage_hyperionship_p":      58,
    "sage_rockforest_p":        55,
    }
    
    return internal_map_to_tab.get(internal_map_id, 0)

ut_tracker_item_layouts = [
    
    {"name": "Shield", "items": [
        "License: Common Shield", 
        "License: Uncommon Shield", 
        "License: Rare Shield", 
        "License: VeryRare Shield", 
        "License: Legendary Shield", 
        "License: Seraph Shield", 
        "License: Rainbow Shield", 
        "License: Unique Shield"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },
    
    {"name": "GrenadeMod", "items": [
        "License: Common GrenadeMod", 
        "License: Uncommon GrenadeMod", 
        "License: Rare GrenadeMod", 
        "License: VeryRare GrenadeMod", 
        "License: Legendary GrenadeMod", 
        "License: Seraph GrenadeMod", 
        "License: Rainbow GrenadeMod", 
        "License: Unique GrenadeMod"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },
    
    {"name": "ClassMod", "items": [
        "License: Common ClassMod", 
        "License: Uncommon ClassMod", 
        "License: Rare ClassMod", 
        "License: VeryRare ClassMod", 
        "License: Legendary ClassMod"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },
    
    {"name": "Relic", "items": [
        "License: Common Relic", 
        "License: Uncommon Relic", 
        "License: Rare Relic", 
        "License: VeryRare Relic", 
        "License: E-Tech Relic", 
        "License: Seraph Relic", 
        "License: Rainbow Relic", 
        "License: Unique Relic"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },
    
    {"name": "Pistol", "items": [
        "License: Common Pistol", 
        "License: Uncommon Pistol", 
        "License: Rare Pistol", 
        "License: VeryRare Pistol", 
        "License: E-Tech Pistol", 
        "License: Legendary Pistol", 
        "License: Seraph Pistol", 
        "License: Pearlescent Pistol", 
        "License: Unique Pistol"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },
    
    {"name": "Shotgun", "items": [
        "License: Common Shotgun", 
        "License: Uncommon Shotgun", 
        "License: Rare Shotgun", 
        "License: VeryRare Shotgun", 
        "License: E-Tech Shotgun", 
        "License: Legendary Shotgun", 
        "License: Seraph Shotgun", 
        "License: Rainbow Shotgun", 
        "License: Pearlescent Shotgun", 
        "License: Unique Shotgun"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },
    
    {"name": "SMG", "items": [
        "License: Common SMG", 
        "License: Uncommon SMG", 
        "License: Rare SMG", 
        "License: VeryRare SMG", 
        "License: E-Tech SMG", 
        "License: Legendary SMG", 
        "License: Seraph SMG", 
        "License: Rainbow SMG", 
        "License: Pearlescent SMG", 
        "License: Unique SMG"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },
    
    {"name": "SniperRifle", "items": [
        "License: Common SniperRifle", 
        "License: Uncommon SniperRifle", 
        "License: Rare SniperRifle", 
        "License: VeryRare SniperRifle", 
        "License: E-Tech SniperRifle", 
        "License: Legendary SniperRifle", 
        "License: Seraph SniperRifle", 
        "License: Rainbow SniperRifle", 
        "License: Pearlescent SniperRifle", 
        "License: Unique SniperRifle"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },
    
    {"name": "AssaultRifle", "items": [
        "License: Common AssaultRifle", 
        "License: Uncommon AssaultRifle", 
        "License: Rare AssaultRifle", 
        "License: VeryRare AssaultRifle", 
        "License: E-Tech AssaultRifle", 
        "License: Legendary AssaultRifle",
        "License: Seraph AssaultRifle", 
        "License: Rainbow AssaultRifle", 
        "License: Pearlescent AssaultRifle", 
        "License: Unique AssaultRifle"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },
    
    {"name": "RocketLauncher", "items": [
        "License: Common RocketLauncher", 
        "License: Uncommon RocketLauncher", 
        "License: Rare RocketLauncher", 
        "License: VeryRare RocketLauncher", 
        "License: E-Tech RocketLauncher", 
        "License: Legendary RocketLauncher", 
        "License: Seraph RocketLauncher", 
        "License: Rainbow RocketLauncher", 
        "License: Pearlescent RocketLauncher", 
        "License: Unique RocketLauncher"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },
    
    {"name": "BlackMarketSDUs", "items": [
        "Max Grenade Count",
        "Max Ammo Pistol", 
        "Max Ammo Shotgun", 
        "Max Ammo SMG", 
        "Max Ammo SniperRifle", 
        "Max Ammo AssaultRifle", 
        "Max Ammo RocketLauncher",  
        "Backpack Upgrade", 
        "Infinite Backpack", 
        "Progressive Weapon Slot"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },
    
    {"name": "AbilityUnlocks", "items": [
        "Progressive Jump",
        "Progressive Sprint",
        "Melee",
        "Crouch",
        "Vehicle Fire", 
        "3 Skill Points", 
        "3 Skill Points (p)", 
        "Progressive Money Cap"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },

    {"name": "Progressive Travel", "items": [
        "Progressive Travel: Base Game",
        "Progressive Travel: Side Area",
        "Progressive Travel: Scarlett DLC",
        "Progressive Travel: Torgue DLC",
        "Progressive Travel: Hammerlock DLC",
        "Progressive Travel: Tina DLC",
        "Progressive Travel: Fight For Sanctuary DLC",
        "Progressive Travel: Headhunters"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },

    {"name": "Base Game Main Areas", "items": [
        "Travel: Sanctuary", 
        "Travel: Southern Shelf", 
        "Travel: Three Horns Divide", 
        "Travel: Frostburn Canyon", 
        "Travel: Three Horns Valley", 
        "Travel: The Dust", 
        "Travel: Bloodshot Stronghold", 
        "Travel: Bloodshot Ramparts", 
        "Travel: Friendship Gulag", 
        "Travel: Tundra Express", 
        "Travel: End of the Line", 
        "Travel: The Fridge", 
        "Travel: Highlands Outwash", 
        "Travel: Highlands", 
        "Travel: Wildlife Exploitation Preserve",  
        "Travel: Opportunity", 
        "Travel: Thousand Cuts", 
        "Travel: The Bunker", 
        "Travel: Control Core Angel", 
        "Travel: Eridium Blight", 
        "Travel: Sawtooth Cauldron", 
        "Travel: Arid Nexus Boneyard", 
        "Travel: Arid Nexus Badlands", 
        "Travel: Hero's Pass", 
        "Travel: Vault of the Warrior"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },

    {"name": "Base Game Side Areas", "items": [
        "Travel: Southern Shelf Bay", 
        "Travel: Southpaw Steam & Power", 
        "Travel: Fink's Slaughterhouse",
        "Travel: The Holy Spirits",  
        "Travel: Sanctuary Hole", 
        "Travel: Caustic Caverns", 
        "Travel: Natural Selection Annex",
        "Travel: Lynchwood", 
        "Travel: Ore Chasm", 
        "Travel: Terramorphous Peak"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },

    {"name": "Scarlett DLC Areas", "items": [
        "Travel: Oasis", 
        "Travel: Wurmwater", 
        "Travel: Hayter's Folly", 
        "Travel: The Rustyards", 
        "Travel: Washburne Refinery", 
        "Travel: Magnys Lighthouse", 
        "Travel: The Leviathan's Lair"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },

    {"name": "Torgue DLC Areas", "items": [
        "Travel: Badass Crater", 
        "Travel: Torgue Arena", 
        "Travel: The Beatdown", 
        "Travel: Pyro Pete's Bar", 
        "Travel: Badass Crater Bar", 
        "Travel: Southern Raceway", 
        "Travel: The Forge"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },

    {"name": "Hammerlock DLC Areas", "items": [
        "Travel: Hunter's Grotto", 
        "Travel: Scylla's Grove", 
        "Travel: Ardorton Station", 
        "Travel: Candlerakk's Crag", 
        "Travel: Terminus"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },

    {"name": "Tina DLC Areas", "items": [
        "Travel: Unassuming Docks", 
        "Travel: Flamerock Refuge", 
        "Travel: The Forest", 
        "Travel: Immortal Woods", 
        "Travel: Mines of Avarice", 
        "Travel: Hatred's Shadow", 
        "Travel: Lair of Infinite Agony", 
        "Travel: Dragon Keep", 
        "Travel: Murderlin's Temple", 
        "Travel: The Winged Storm"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },

    {"name": "FFS DLC Areas", "items": [
        "Travel: FFS Intro Sanctuary", 
        "Travel: The Backburner", 
        "Travel: Dahl Abandon", 
        "Travel: The Burrows", 
        "Travel: Helios Fallen", 
        "Travel: Mt. Scarab Research Center", 
        "Travel: FFS Boss Fight", 
        "Travel: Writhing Deep"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) },

    {"name": "Headhunter Areas", "items": [
        "Travel: Hallowed Hollow", 
        "Travel: Gluttony Gulch", 
        "Travel: Marcus's Mercenary Shop", 
        "Travel: Rotgut Distillery", 
        "Travel: Wam Bam Island", 
        "Travel: Digistruct Peak"
    ], "orientation": "lr", "cols": 10, "item_size": (48, 48) }
]