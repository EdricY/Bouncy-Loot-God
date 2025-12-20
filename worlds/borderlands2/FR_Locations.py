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
    "Hayters": "HaytersFolly",
    "Hayter's": "HaytersFolly",
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
            "Level 2": "DigistructPeak",
            "Level 3": "DigistructPeak",
            "Level 4": "SouthernShelf",
            "Level 5": "SouthernShelf",
            "Level 6": "SouthernShelf",
            "Level 7": "SouthernShelf",
            "Level 8": "ThreeHornsDivide",
            "Level 9": "ThreeHornsDivide",
            "Level 10": "FrostburnCanyon",
            "Level 11": "FrostburnCanyon",
            "Level 12": "Dust",
            "Level 13": "BloodshotStronghold",
            "Level 14": "BloodshotStronghold",
            "Level 15": "TundraExpress",
            "Level 16": "TundraExpress",
            "Level 17": "Fridge",
            "Level 18": "Highlands",
            "Level 19": "WildlifeExploitationPreserve",
            "Level 20": "WildlifeExploitationPreserve",
            "Level 21": "ThousandCuts",
            "Level 22": "ThousandCuts",
            "Level 23": "Opportunity",
            "Level 24": "Opportunity",
            "Level 25": "Bunker",
            "Level 26": "Bunker",
            "Level 27": "EridiumBlight",
            "Level 28": "SawtoothCauldron",
            "Level 29": "AridNexusBoneyard",
            "Level 30": "AridNexusBadlands",

            #Uncommon Items
            "Uncommon Shield": "SouthernShelf Combat",
            "Uncommon GrenadeMod": "SouthernShelf Combat",
            "Uncommon ClassMod": "BloodshotStronghold Combat",
            "Uncommon Relic": "BloodshotStronghold Combat",
            "Uncommon Pistol": "SouthernShelf Combat",
            "Uncommon Shotgun": "SouthernShelf Combat",
            "Uncommon SMG": "SouthernShelf Combat",
            "Uncommon SniperRifle": "SouthernShelf Combat",
            "Uncommon AssaultRifle": "SouthernShelf Combat",
            "Uncommon RocketLauncher": "BloodshotStronghold Combat",

            #Rare Items
            "Rare Shield": "BloodshotStronghold Combat",
            "Rare GrenadeMod": "BloodshotStronghold Combat",
            "Rare ClassMod": "BloodshotStronghold Combat",
            "Rare Relic": "BloodshotStronghold Combat",
            "Rare Pistol": "BloodshotStronghold Combat",
            "Rare Shotgun": "BloodshotStronghold Combat",
            "Rare SMG": "BloodshotStronghold Combat",
            "Rare SniperRifle": "BloodshotStronghold Combat",
            "Rare AssaultRifle": "BloodshotStronghold Combat",
            "Rare RocketLauncher": "BloodshotStronghold Combat",

            #VeryRare Items
            "VeryRare Shield": "Opportunity Combat",
            "VeryRare GrenadeMod": "Opportunity Combat",
            "VeryRare ClassMod": "Opportunity Combat",
            "VeryRare Relic": "Opportunity Combat",
            "VeryRare Pistol": "Opportunity Combat",
            "VeryRare Shotgun": "Opportunity Combat",
            "VeryRare SMG": "Opportunity Combat",
            "VeryRare SniperRifle": "Opportunity Combat",
            "VeryRare AssaultRifle": "Opportunity Combat",
            "VeryRare RocketLauncher": "Opportunity Combat",

            #E-Tech Items
            "E-Tech Relic": "HerosPass Combat",
            "E-Tech Pistol": "HerosPass Combat",
            "E-Tech Shotgun": "HerosPass Combat",
            "E-Tech SMG": "HerosPass Combat",
            "E-Tech SniperRifle": "HerosPass Combat",
            "E-Tech AssaultRifle": "HerosPass Combat",
            "E-Tech RocketLauncher": "HerosPass Combat",

            #Legendary Items
            "Legendary Shield": "WindshearWaste Combat",
            "Legendary GrenadeMod": "SouthernShelf Combat",
            "Legendary ClassMod": "VaultOfTheWarrior Combat",
            "Legendary Pistol": "WindshearWaste Combat",
            "Legendary Shotgun": "Fridge Combat",
            "Legendary SMG": "FrostburnCanyon Combat",
            "Legendary SniperRifle": "Dust Combat",
            "Legendary AssaultRifle": "SouthernShelfBay Combat",
            "Legendary RocketLauncher": "FrostburnCanyon Combat",

            #Unique Items
            "Unique Shield": "HuntersGrotto Combat",
            "Unique GrenadeMod": "SouthernShelf Combat",
            #"Unique ClassMod": "VaultOfTheWarrior Combat",
            "Unique Pistol": "SouthernShelf Combat",
            "Unique Shotgun": "SouthpawSteam&Power Combat",
            "Unique SMG": "SouthpawSteam&Power Combat",
            "Unique SniperRifle": "SouthpawSteam&Power Combat",
            "Unique AssaultRifle": "CandlerakksCrag Combat",
            "Unique RocketLauncher": "AridNexusBadlands Combat",

            "Symbol DahlAbandon: The Veiny Shaft": "HeliosFallen",

            # enemies
            "Enemy FrostburnCanyon: Spycho": "AridNexusBoneyard",
            "Enemy UnassumingDocks: Unmotivated Golem": "MinesOfAvarice",
            "Enemy Forest: Arguk the Butcher": "ImmortalWoods",
            "Enemy DahlAbandon: The Dark Web": "HeliosFallen",
            "Enemy Burrows: Lt. Angvar": "Mt.ScarabResearchCenter",
            "Enemy DahlAbandon: Lt. Bolson": "Mt.ScarabResearchCenter",
            "Enemy HeliosFallen: Lt. Tetra": "Mt.ScarabResearchCenter",

            "Vending ThreeHornsValley Motel: Guns": "FrostburnCanyon",
            "Vending ThreeHornsValley Motel: Ammo Dump": "FrostburnCanyon",
            "Vending ThreeHornsValley Motel: Zed's Meds": "FrostburnCanyon",

            "Quest Washburne: Hyperius the Invincible": "LeviathansLair",
            "Quest Hayters: Master Gee the Invincible": "LeviathansLair",
            "Quest PyroPetesBar: Pyro Pete the Invincible": "Forge",
            "Quest Beatdown: Number One Fan": "SouthernRaceway",
            "Quest Beatdown: Mother-Lover": "SouthernRaceway",
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
            "Generic: Badass": "Sanctuary",
}


coop_locations = {
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

raidboss_regions = {
    "WingedStorm",
    "WrithingDeep",
    "TerramorphousPeak",
}
raidboss_locations = {
    # Terramorphous, Dragons, Haderax
    "Enemy TundraExpress: Vermivorous the Invincible",
    "Enemy Washburne Refinery: Hyperius",
    "Enemy Hayter's Folly: Master Gee",
    "Enemy Pyro Pete's Bar: Pyro Pete the Invincible",
    "Enemy CandlerakksCrag: Voracidous the Invincible",
    "Enemy HuntersGrotto: Dexiduous the Invincible",
    "Enemy WamBamIsland: Son of Crawmerax Raid Boss",

    "Challenge ScarlettDLC: Hyperius the Not-So-Invincible",
    "Challenge ScarlettDLC: Master Worm Food",
    "Challenge TorgueDLC: Pete the Invincible Defeated"
    "Challenge HammerlockDLC: Voracidous the Invincible",

    "Quest Washburne: Hyperius the Invincible",
    "Quest Hayters: Master Gee the Invincible",
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
