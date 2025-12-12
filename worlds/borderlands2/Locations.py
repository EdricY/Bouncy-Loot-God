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
    "Crag": "CandlerakksCragg",
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
    "Hayters": "HaytorsFolly",
    "Warrior": "VaultOfTheWarrior",
    "WarriorVault": "VaultOfTheWarrior",
    "Handsome": "DragonKeep",
    "Shadow": "HatredsShadow",
    "Agony": "LairOfInfiniteAgony",
    "Lair": "LairOfInfiniteAgony",
    "Pyro": "PyroPetesBar",
    "Pete's": "PyroPetesBar",
    "Murderlin's": "MurderlinsTemple",
    "Arena": "TorgueArena",
    "Hallowed": "HallowedHollow",
    "Control": "ControlCoreAngel"
}

region_exceptions = {
    "Common Pistol": "WindshearWaste",
    "Common Shield": "SouthernShelf",
    "Level 2": "DigistructPeak",
    "Level 3": "DigistructPeak",
    "Level 4": "SouthernShelf",
    "Enemy FrostburnCanyon: Spycho": "AridNexusBoneyard",
    "Symbol ThreeHornsValley: Slums Wall": "BloodshotStronghold",
    "Symbol Bloodshot: Pizza Intercom": "BloodshotRamparts",
    "Symbol Opportunity: Construction Site":    "Terminus",
    "Symbol DahlAbandon: The Veiny Shaft": "HeliosFallen",

    #enemies
    "Enemy ThreeHornsDivide: Boll": "FrostburnCanyon",
    "Enemy ThreeHornsValley: Doc Mercy":            "Sanctuary",
    "Enemy Dust: Gettle":                       "Highlands",
    "Enemy Dust: Mobley":                       "Highlands",
    "Enemy ThreeHornsValley: Bad Maw":  "BloodshotStronghold",
    "Enemy Dust: McNally":              "Opportunity",
    "Enemy Dust: Mick/Tector":              "Highlands",
    "Enemy BloodshotStronghold: Dan":                  "BloodshotRamparts",
    "Enemy BloodshotStronghold: Lee":                  "BloodshotRamparts",
    "Enemy BloodshotStronghold: Mick":                 "BloodshotRamparts",
    "Enemy BloodshotStronghold: Ralph":                "BloodshotRamparts",
    "Enemy BloodshotStronghold: Flinter":              "BloodshotRamparts",
    "Enemy TundraExpress: Prospector Zeke":  "Highlands",
    "Enemy Fridge: LaneyWhite":              "Highlands",
    "Enemy Fridge: Rakkman":                 "Highlands",
    "Enemy Fridge: SmashHead":               "Highlands",
    "Enemy Fridge: Sinkhole":                "Highlands",
    "Enemy CausticCaverns: Blue":            "Highlands",
    "Enemy Lynchwood: DukinosMom":           "EridiumBlight",
    "Enemy Lynchwood: MadDog":               "Opportunity",
    "Enemy Lynchwood: SheriffNisha":         "Opportunity",
    "Enemy Lynchwood: DeputyWinger":         "Opportunity",
    "Enemy Opportunity: ForemanJasper":         "Bunker",
    "Enemy Opportunity: JackBodyDouble":        "Bunker",
    "Enemy Unassuming Docks: Unmotivated Golem": "ImmortalWoods",
    "Enemy The Forest: Arguk the Butcher":       "ImmortalWoods",
    "Enemy Dahl Abandon: The Dark Web":     "HeliosFallen",
    "Enemy The Burrows: Lt. Angvar":  "Mt.ScarabResearchCenter",
    "Enemy Dahl Abandon: Lt. Bolson": "Mt.ScarabResearchCenter",
    "Enemy Helios Fallen: Lt. Tetra": "Mt.ScarabResearchCenter",
    "Enemy Mt Scarab: Lt. Hoffman":   "Mt.ScarabResearchCenter",

    #Quests
    #Lynchwood quests
    "Quest Lynchwood: Demon Hunter":    "EridiumBlight",
    "Quest Lynchwood: 3:10 to Kaboom": "Opportunity",
    "Quest Lynchwood: Breaking the Bank": "Opportunity",
    "Quest Lynchwood: Animal Rescue: Medicine": "Opportunity",
    "Quest Lynchwood: Animal Rescue: Food": "Opportunity",
    "Quest Lynchwood: Animal Rescue: Shelter": "Opportunity",
    "Quest Lynchwood: Showdown": "Opportunity",
    #Dust quests
    "Quest Dust: Clan War: First Place": "Highlands",
    "Quest Dust: Clan War: Trailer Trashing": "Highlands",
    "Quest Dust: Clan War: Zafords vs. Hodunks": "Highlands",
    "Quest Dust: Rakkaholics Anonymous": "WildlifeExploitationPreserve",
    "Quest Dust: The Good, the Bad, and the Mordecai": "Highlands",
    #Sanctuary quests
    "Quest Sanctuary: Bearer of Bad News":  "EridiumBlight",
    "Quest Sanctuary: BFFs": "EridiumBlight",
    "Quest Sanctuary: Won't Get Fooled Again": "Highlands",
    "Quest Sanctuary: Claptrap's Birthday Bash!": "Highlands",

    "Quest ThreeHornsDivide: In Memoriam":  "Sanctuary",
    #Caustic Caverns Quests
    "Quest CausticCaverns: Minecart Mischief":  "Highlands",
    "Quest CausticCaverns: Perfectly Peaceful": "Highlands",
    "Quest CausticCaverns: Safe and Sound": "Highlands",
    "Quest Tundra Express: Mine, All Mine": "Highlands",
    "Quest Tundra Express: The Pretty Good Train Robbery": "Highlands",
    #Fridge quests
    "Quest Fridge: The Cold Shoulder":   "Highlands",
    "Quest Fridge: Swallowed Whole":   "Highlands",
    "Quest Fridge: Note for Self-Person":   "Highlands",
    "Quest ThreeHornsValley: Medical Mystery": "FrostburnCanyon",
    "Quest ThreeHornsValley: Medical Mystery: X-Com-municate": "FrostburnCanyon",

    #DLC1 Quests
    "Quest Washburne: Hyperius the Invincible": "Leviathan",
    "Quest Hayters: Master Gee the Invincible": "Leviathan",

    #DLC2 Quests
    "Quest PyroPetesBar: Pyro Pete the Invincible": "Forge",

    #DLC3 Quests
    "Quest CandlerakksCrag: Voracidous the Invincible": "Terminus"

}

def get_region_from_loc_name(loc_name):
    exception_loc = region_exceptions.get(loc_name)
    if exception_loc is not None:
        return exception_loc

    pieces = re.split(r'[ :]', loc_name)

    if len(pieces) < 2:
        return "Sanctuary"

    second_word = pieces[1]
    if second_word in region_data_table.keys():
        return second_word

    variant_translation = region_name_variants.get(second_word)
    if variant_translation in region_data_table.keys():
        return variant_translation

    # print("didn't find region for loc: " + loc_name)
    return "AridNexusBoneyard"


location_data_table: Dict[str, Borderlands2LocationData] = {
    name: Borderlands2LocationData(region=get_region_from_loc_name(name), address=bl2_base_id + loc_id, description="")
    for name, loc_id in loc_name_to_id.items()
}

location_name_to_id = {name: data.address for name, data in location_data_table.items() if data.address is not None}

location_descriptions = {name: data.description for name, data in location_data_table.items() if
                         data.address is not None}
