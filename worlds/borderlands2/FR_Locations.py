from typing import Dict, NamedTuple, Optional
import re


from BaseClasses import Location
from .archi_defs import loc_name_to_id
from .Items import bl2_base_id
from .Regions import region_data_table

class Borderlands2Location(Location):
    game = "Borderlands 2"




class Borderlands2LocationData(NamedTuple):
    region: str
    address: Optional[int] = None
    description: Optional[str] = None


# want to pull regions from the location names directly. So store some variants here
region_name_variants = {
    "Fink's": "FinksSlaughterhouse",
    "Bloodshot": "BloodshotStronghold",
    "Stronghold": "BloodshotStronghold",
    "Ramparts": "BloodshotRamparts",
    "Tundra": "TundraExpress",
    "Outwash": "HighlandsOutwash",
    "Caustic": "CausticCaverns",
    "Caverns": "CausticCaverns",
    "Thousand": "ThousandCuts",
    "Blight": "EridiumBlight",
    "Eridium": "EridiumBlight",
    "Sawtooth": "SawtoothCauldron",
    "Frostburn": "FrostburnCanyon",
    "Southpaw": "SouthpawSteam&Power",
    "Preserve": "WildlifeExploitationPreserve",
    "WildlifePreserve": "WildlifeExploitationPreserve",
    "Creature": "NaturalSelectionAnnex",
    "CreatureSlaughter": "NaturalSelectionAnnex",
    "Boneyard": "AridNexusBoneyard",
    "Badlands": "AridNexusBadlands",
    "BadassBar": "BadassCraterBar",
    "Raceway": "SouthernRaceway",
    "Grotto": "HuntersGrotto",
    "Crater": "BadassCrater",
    "Leviathan": "LeviathansLair",
    "Magnys": "MagnysLighthouse",
    "Washburne": "WashburneRefinery",
    "Ardorton": "ArdortonStation",
    "Crag": "CandlerakksCrag",
    "Scylla's": "ScyllasGrove",
    "Flamerock": "FlamerockRefuge",
    "Immortal": "ImmortalWoods",
    "Avarice": "MinesOfAvarice",
    "TheBurrows": "Burrows",
    "MtScarab": "Mt.ScarabResearchCenter",
    "Mt.Scarab": "Mt.ScarabResearchCenter",
    "GlutGulch": "GluttonyGulch",
    "Distillery": "RotgutDistillery",
    "MercenaryDay": "MarcusMercenaryShop",
    "Rotgut": "RotgutDistillery",
    "WamBam": "WamBamIsland",
    "Digistruct": "DigistructPeak",
    "DigistructInner": "DigistructPeakInner",
    "Terramorphous": "TerramorphousPeak",
    "Haytors": "HaytorsFolly",
    "Haytor's": "HaytorsFolly",
    "Warrior": "VaultOfTheWarrior",
    "WarriorVault": "VaultOfTheWarrior",
    "Handsome": "DragonKeep",
    "Shadow": "HatredsShadow",
    "Hatred's": "HatredsShadow",
    "Agony": "LairOfInfiniteAgony",
    "Lair": "LairOfInfiniteAgony",
    "Pyro": "PyroPetesBar",
    "Pete's": "PyroPetesBar",
    "Murderlin's": "MurderlinsTemple",
    "Arena": "TorgueArena",
    "Hallowed": "HallowedHollow",
    "Control": "ControlCoreAngel",
    "Paradise": "FFSBossFight",
    "DigiPeak": "DigistructPeak",
    "DigiPeakInner": "DigistructPeakInner",
    "LilithDLC": "FFSBossFight",
    "TinaDLC": "DragonKeep",
    "ScarlettDLC": "LeviathansLair",
    "HammerlockDLC": "Terminus",
    "TorgueDLC": "Forge",
    "Combat": "SouthernShelf",
    "Grenade": "SouthernShelf",
    "Money": "SouthernShelf",
}

region_exceptions = {
    #Levels
    "Level 2":  "WindshearWaste Combat",
    "Level 3": "SouthernShelf Combat",
    "Level 4": "SouthernShelf Combat",
    "Level 5": "SouthernShelf Combat",
    "Level 6": "SouthernShelf Combat",
    "Level 7": "ThreeHornsDivide Combat",
    "Level 8": "FrostburnCanyon Combat",
    "Level 9": "FrostburnCanyon Combat",
    "Level 10": "ThreeHornsValley Combat",
    "Level 11": "BloodshotStronghold Combat",
    "Level 12": "BloodshotStronghold Combat",
    "Level 13": "BloodshotStronghold Combat",
    "Level 14": "TundraExpress Combat",
    "Level 15": "TundraExpress Combat",
    "Level 16": "TundraExpress Combat",
    "Level 17": "HighlandsOutwash Combat",
    "Level 18": "Highlands Combat",
    "Level 19": "WildlifeExploitationPreserve Combat",
    "Level 20": "ThousandCuts Combat",
    "Level 21": "Opportunity Combat",
    "Level 22": "Opportunity Combat",
    "Level 23": "Bunker Combat",
    "Level 24": "Dust Combat",
    "Level 25": "Lynchwood Combat",
    "Level 26": "EridiumBlight Combat",
    "Level 27": "EridiumBlight Combat",
    "Level 28": "AridNexusBoneyard Combat",
    "Level 29": "AridNexusBoneyard Combat",
    "Level 30": "HerosPass Combat",

    #Common Items
    "Common Shield":    "SouthernShelf Combat",
    "Common Grenade Mod": "SouthernShelf Combat",
    "Common Class Mod": "FrostburnCanyon Combat",
    "Common Relic": "BloodshotStronghold Combat",
    "Common Pistol": "WindshearWaste Combat",
    "Common Shotgun": "ThreeHornsDivide Combat",
    "Common SMG": "ThreeHornsDivide Combat",
    "Common Sniper Rifle": "ThreeHornsDivide Combat",
    "Common Assault Rifle": "SouthernShelf Combat",
    "Common Rocket Launcher": "BloodshotStronghold Combat",

    #Uncommon Items
    "Uncommon Shield": "SouthernShelf Combat",
    "Uncommon Grenade Mod": "SouthernShelf Combat",
    "Uncommon Class Mod": "BloodshotStronghold Combat",
    "Uncommon Relic": "BloodshotStronghold Combat",
    "Uncommon Pistol": "SouthernShelf Combat",
    "Uncommon Shotgun": "SouthernShelf Combat",
    "Uncommon SMG": "SouthernShelf Combat",
    "Uncommon Sniper Rifle": "SouthernShelf Combat",
    "Uncommon Assault Rifle": "SouthernShelf Combat",
    "Uncommon Rocket Launcher": "BloodshotStronghold Combat",

    #Rare Items
    "Rare Shield": "BloodshotStronghold Combat",
    "Rare Grenade Mod": "BloodshotStronghold Combat",
    "Rare Class Mod": "BloodshotStronghold Combat",
    "Rare Relic": "BloodshotStronghold Combat",
    "Rare Pistol": "BloodshotStronghold Combat",
    "Rare Shotgun": "BloodshotStronghold Combat",
    "Rare SMG": "BloodshotStronghold Combat",
    "Rare Sniper Rifle": "BloodshotStronghold Combat",
    "Rare Assault Rifle": "BloodshotStronghold Combat",
    "Rare Rocket Launcher": "BloodshotStronghold Combat",

    #VeryRare Items
    "VeryRare Shield": "Opportunity Combat",
    "VeryRare Grenade Mod": "Opportunity Combat",
    "VeryRare Class Mod": "Opportunity Combat",
    "VeryRare Relic": "Opportunity Combat",
    "VeryRare Pistol": "Opportunity Combat",
    "VeryRare Shotgun": "Opportunity Combat",
    "VeryRare SMG": "Opportunity Combat",
    "VeryRare Sniper Rifle": "Opportunity Combat",
    "VeryRare Assault Rifle": "Opportunity Combat",
    "VeryRare Rocket Launcher": "Opportunity Combat",

    #E-Tech Items
    "E-Tech Relic": "AridNexusBadlands Combat",
    "E-Tech Pistol": "AridNexusBadlands Combat",
    "E-Tech Shotgun": "AridNexusBadlands Combat",
    "E-Tech SMG": "AridNexusBadlands Combat",
    "E-Tech Sniper Rifle": "AridNexusBadlands Combat",
    "E-Tech Assault Rifle": "AridNexusBadlands Combat",
    "E-Tech Rocket Launcher": "AridNexusBadlands Combat",

    #Legendary Items
    "Legendary Shield": "WildlifeExploitationPreserve Combat",
    "Legendary Grenade Mod": "SouthernShelf Combat",
    "Legendary Class Mod": "VaultOfTheWarrior Combat",
    "Legendary Pistol": "WindshearWaste Combat",
    "Legendary Shotgun": "Fridge Combat",
    "Legendary SMG": "FrostburnCanyon Combat",
    "Legendary Sniper Rifle": "Dust Combat",
    "Legendary Assault Rifle": "SouthernShelfBay Combat",
    "Legendary Rocket Launcher": "FrostburnCanyon Combat",

    #Unique Items
    "Unique Shield": "HuntersGrotto Combat",
    "Unique Grenade Mod": "SouthernShelf Combat",
    #"Unique ClassMod": "VaultOfTheWarrior Combat",
    "Unique Relic": "Burrows Combat",
    "Unique Pistol": "SouthernShelf Combat",
    "Unique Shotgun": "SouthpawSteam&Power Combat",
    "Unique SMG": "SouthpawSteam&Power Combat",
    "Unique Sniper Rifle": "SouthpawSteam&Power Combat",
    "Unique Assault Rifle": "CandlerakksCrag Combat",
    "Unique Rocket Launcher": "AridNexusBadlands Combat",

    "Symbol DahlAbandon: The Veiny Shaft": "HeliosFallen",

    #Quests that need to be moved around
    "Quest Sanctuary: The Name Game":   "ThreeHornsDivide",

    # enemies
    "Enemy HolySpirits: Bagman":                    "Dust",
    "Enemy Frostburn Canyon: Spycho":               "AridNexusBoneyard",
    "Enemy UnassumingDocks: Unmotivated Golem":     "MinesOfAvarice",
    "Enemy Forest: Arguk the Butcher":              "ImmortalWoods",
    "Enemy DahlAbandon: The Dark Web":              "HeliosFallen",
    "Enemy Burrows: Lt. Angvar":                    "Mt.ScarabResearchCenter",
    "Enemy DahlAbandon: Lt. Bolson":                "Mt.ScarabResearchCenter",
    "Enemy HeliosFallen: Lt. Tetra":                "Mt.ScarabResearchCenter",

    "Vending ThreeHornsValley Motel: Guns":         "FrostburnCanyon",
    "Vending ThreeHornsValley Motel: Ammo Dump":    "FrostburnCanyon",
    "Vending ThreeHornsValley Motel: Zed's Meds":   "FrostburnCanyon",

    "Quest Washburne: Hyperius the Invincible":         "LeviathansLair",
    "Quest Haytors: Master Gee the Invincible":         "LeviathansLair",
    "Quest PyroPetesBar: Pyro Pete the Invincible":     "Forge",
    "Quest Beatdown: Number One Fan":                   "SouthernRaceway",
    "Quest Beatdown: Mother-Lover":                     "SouthernRaceway",
    "Quest CandlerakksCrag: Voracidous the Invincible": "Terminus",

    "Generic: Skag": "ThreeHornsValley",
    "Generic: Rakk": "SouthernShelf",
    "Generic: Bullymong": "SouthernShelf",
    "Generic: Psycho": "SouthernShelf",
    "Generic: Rat": "Fridge",
    "Generic: Spiderant": "FrostburnCanyon",
    "Generic: Varkid": "TundraExpress",
    "Generic: Goliath": "ThousandCuts",
    "Generic: Marauder": "SouthernShelf",
    "Generic: Stalker": "HighlandsOutwash",
    "Generic: Midget": "ThreeHornsValley",
    "Generic: Nomad": "ThreeHornsValley",
    "Generic: Thresher": "CausticCaverns",
    "Generic: Badass": "FrostburnCanyon",

    #Vending locked behind combat
    "Vending Fridge Elevator: Ammo Dump": "Fridge Combat",
    "Vending Fridge Elevator: Zed's Meds": "Fridge Combat",


    #Chests locked behind combat
    "Chest RotgutDistillery: Rectory 1": "RotgutDistillery Combat",
    "Chest RotgutDistillery: Rectory 2": "RotgutDistillery Combat",
    "Chest RotgutDistillery: Thresher Tails": "RotgutDistillery Combat",
    "Chest AridNexusBadlands: Hyperion Info Stockade": "AridNexusBadlands Combat",
    "Chest Bunker: Back Room":  "Bunker Combat",

}


fr_coop_locations = {
    # 1 = impossible, 2 = difficult

    "Challenge Misc: Haters Gonna Hate": 1,
    "Challenge Money: Psst, Hey Buddy...": 1,
    "Challenge Dust: I've Got a Crush on You": 1,
    "Challenge Lynchwood: Duel of Death": 1,
    "Challenge Recovery: This Is No Time for Lazy!": 1,

    "Challenge Opportunity: Top o' the World": 2,
    "Challenge TerramorphousPeak: Cult of the Vault": 2,
    "Symbol TerramorphousPeak: Dropdown": 2,
}

fr_raidboss_regions = {
    "WingedStorm",
    "WrithingDeep",
    "TerramorphousPeak",
}
fr_raidboss_locations = {
    # Terramorphous, Dragons, Haderax
    "Enemy TundraExpress: Vermivorous the Invincible",
    "Enemy Washburne Refinery: Hyperius",
    "Enemy Haytor's Folly: Master Gee",
    "Enemy Pyro Pete's Bar: Pyro Pete the Invincible",
    "Enemy CandlerakksCrag: Voracidous the Invincible",
    "Enemy HuntersGrotto: Dexiduous the Invincible",
    "Enemy WamBamIsland: Son of Crawmerax Raid Boss",

    "Challenge ScarlettDLC: Hyperius the Not-So-Invincible",
    "Challenge ScarlettDLC: Master Worm Food",
    "Challenge TorgueDLC: Pete the Invincible Defeated"
    "Challenge HammerlockDLC: Voracidous the Invincible",

    "Quest Washburne: Hyperius the Invincible",
    "Quest Haytors: Master Gee the Invincible",
    "Quest PyroPetesBar: Pyro Pete the Invincible",
    "Quest CandlerakksCrag: Voracidous the Invincible",
    "Quest WingedStorm: Raiders of the Last Boss",

    "Chest WamBamIsland: Raid Reward #4",
    "Chest WamBamIsland: Raid Reward #5",
    "Chest WamBamIsland: Raid Reward #3",
    "Chest WamBamIsland: Raid Reward #7",
    "Chest WamBamIsland: Raid Reward #6",
    "Chest WamBamIsland: Raid Reward #2",
    "Chest WamBamIsland: Raid Reward #1",
}





def FR_get_region_from_loc_name(loc_name):
    exception_loc = region_exceptions.get(loc_name)
    if exception_loc is not None:
        return exception_loc

    pieces = re.split(r'[ :]', loc_name)

    if len(pieces) <= 2:
        return "Sanctuary"

    second_word = pieces[1]
    if second_word in region_data_table.keys():
        return second_word

    variant_translation = region_name_variants.get(second_word)
    if variant_translation in region_data_table.keys():
        return variant_translation

    # print("didn't find region for loc: " + loc_name)
    return "AridNexusBoneyard"

fr_location_data_table: Dict[str, Borderlands2LocationData] = {
    name: Borderlands2LocationData(region=FR_get_region_from_loc_name(name), address=bl2_base_id + loc_id, description="")
    for name, loc_id in loc_name_to_id.items()
}

fr_location_name_to_id = {name: data.address for name, data in fr_location_data_table.items() if data.address is not None}

fr_location_descriptions = {name: data.description for name, data in fr_location_data_table.items() if
                         data.address is not None}
