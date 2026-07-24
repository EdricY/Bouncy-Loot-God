from typing import Dict, List, NamedTuple, Union


class Borderlands1RegionData(NamedTuple):
    name: str = ""
    min_level: int = 0 # the lowest level you could begin farming exp in this area
    max_level: int = 0 # the highest expected level you could farm exp in this area up to
    travel_item_name: str = ""
    connecting_regions: List[str] = []
    story_req_regions: List[str] = []
    dlc_group: str = "basegame"

region_data_table: Dict[str, Borderlands1RegionData] = {
    "Menu": Borderlands1RegionData("Menu", 0, 0, "", [
        "WindshearWaste",
        "DigistructPeak",
        "FFSIntroSanctuary",
        "UnassumingDocks",
        "BadassCrater",
        "Oasis",
        "HuntersGrotto",
        "HallowedHollow",
        "GluttonyGulch",
        "MarcusMercenaryShop",
        "RotgutDistillery",
        "WamBamIsland",
    ], dlc_group= "menu"),
    "WindshearWaste": Borderlands1RegionData("WindshearWaste", 0, 3, "", ["SouthernShelf"]),
    "SouthernShelf": Borderlands1RegionData("SouthernShelf", 1, 5, "Travel: Southern Shelf", ["SouthernShelfBay", "ThreeHornsDivide"]),
    "SouthernShelfBay": Borderlands1RegionData("SouthernShelfBay", 4, 6, "Travel: Southern Shelf Bay", [], dlc_group="basegame_side"),
    "ThreeHornsDivide": Borderlands1RegionData("ThreeHornsDivide", 6, 10, "Travel: Three Horns Divide", ["ThreeHornsValley", "Sanctuary", "FrostburnCanyon", "SanctuaryHole", "TundraExpress"]),
    "Sanctuary": Borderlands1RegionData("Sanctuary", 7, 7, "Travel: Sanctuary", []),
    "FrostburnCanyon": Borderlands1RegionData("FrostburnCanyon", 9, 11, "Travel: Frostburn Canyon", []),
    "ThreeHornsValley": Borderlands1RegionData("ThreeHornsValley", 8, 10, "Travel: Three Horns Valley", ["SouthpawSteam&Power", "Dust", "Fridge", "BloodshotStronghold"]),
    "SouthpawSteam&Power": Borderlands1RegionData("SouthpawSteam&Power", 8, 9, "Travel: Southpaw Steam & Power", [], dlc_group="basegame_side"),
    "Dust": Borderlands1RegionData("Dust", 9, 12, "Travel: The Dust", ["Lynchwood", "FriendshipGulag", "EridiumBlight", "Highlands"]),
    "BloodshotStronghold": Borderlands1RegionData("BloodshotStronghold", 12, 14, "Travel: Bloodshot Stronghold", ["BloodshotRamparts"], story_req_regions=["Dust", "FrostburnCanyon", "Sanctuary"]),
    "BloodshotRamparts": Borderlands1RegionData("BloodshotRamparts", 12, 14, "Travel: Bloodshot Ramparts", []),
    "FriendshipGulag": Borderlands1RegionData("FriendshipGulag", 12, 14, "Travel: Friendship Gulag", [], story_req_regions=["BloodshotStronghold"]),
    "TundraExpress": Borderlands1RegionData("TundraExpress", 13, 16, "Travel: Tundra Express", ["EndOfTheLine"], story_req_regions=["BloodshotRamparts"]),
    "EndOfTheLine": Borderlands1RegionData("EndOfTheLine", 13, 16, "Travel: End of the Line", []),
    "Fridge": Borderlands1RegionData("Fridge", 15, 17, "Travel: The Fridge", ["FinksSlaughterhouse", "HighlandsOutwash"], story_req_regions=["EndOfTheLine"]),
    "FinksSlaughterhouse": Borderlands1RegionData("FinksSlaughterhouse", 15, 17, "Travel: Fink's Slaughterhouse", [], dlc_group="basegame_side"),
    "HighlandsOutwash": Borderlands1RegionData("HighlandsOutwash", 15, 17, "Travel: Highlands Outwash", ["Highlands"]),
    "Highlands": Borderlands1RegionData("Highlands", 16, 19, "Travel: Highlands", ["HolySpirits", "WildlifeExploitationPreserve", "ThousandCuts", "Opportunity"], story_req_regions=["HighlandsOutwash"]),
    "HolySpirits": Borderlands1RegionData("HolySpirits", 18, 18, "Travel: The Holy Spirits", [], dlc_group="basegame_side"),
    "SanctuaryHole": Borderlands1RegionData("SanctuaryHole", 13, 15, "Travel: Sanctuary Hole", ["CausticCaverns"], story_req_regions=["EndOfTheLine"], dlc_group="basegame_side"),
    "CausticCaverns": Borderlands1RegionData("CausticCaverns", 16, 18, "Travel: Caustic Caverns", [], dlc_group="basegame_side"),
    "WildlifeExploitationPreserve": Borderlands1RegionData("WildlifeExploitationPreserve", 18, 21, "Travel: Wildlife Exploitation Preserve", ["NaturalSelectionAnnex"]),
    "NaturalSelectionAnnex": Borderlands1RegionData("NaturalSelectionAnnex", 20, 21, "Travel: Natural Selection Annex", [], dlc_group="basegame_side"),
    "ThousandCuts": Borderlands1RegionData("ThousandCuts", 20, 23, "Travel: Thousand Cuts", ["Bunker", "TerramorphousPeak"]),
    "Lynchwood": Borderlands1RegionData("Lynchwood", 24, 26, "Travel: Lynchwood", [], dlc_group="basegame_side"),
    "Opportunity": Borderlands1RegionData("Opportunity", 20, 24, "Travel: Opportunity", []),
    "Bunker": Borderlands1RegionData("Bunker", 24, 26, "Travel: The Bunker", ["ControlCoreAngel"], story_req_regions=["WildlifeExploitationPreserve", "Opportunity"]),
    "ControlCoreAngel": Borderlands1RegionData("ControlCoreAngel", 25, 25, "Travel: Control Core Angel", []),
    "EridiumBlight": Borderlands1RegionData("EridiumBlight", 25, 27, "Travel: Eridium Blight", ["OreChasm", "SawtoothCauldron", "AridNexusBoneyard", "HerosPass"], story_req_regions=["ControlCoreAngel"]),
    "OreChasm": Borderlands1RegionData("OreChasm", 25, 27, "Travel: Ore Chasm", [], dlc_group="basegame_side"),
    "SawtoothCauldron": Borderlands1RegionData("SawtoothCauldron", 25, 28, "Travel: Sawtooth Cauldron"),
    "AridNexusBoneyard": Borderlands1RegionData("AridNexusBoneyard", 26, 29, "Travel: Arid Nexus Boneyard", ["AridNexusBadlands"], story_req_regions=["SawtoothCauldron"]),
    "AridNexusBadlands": Borderlands1RegionData("AridNexusBadlands", 26, 30, "Travel: Arid Nexus Badlands"),
    "HerosPass": Borderlands1RegionData("HerosPass", 29, 30, "Travel: Hero's Pass", ["VaultOfTheWarrior"], story_req_regions=["AridNexusBadlands"]),
    "VaultOfTheWarrior": Borderlands1RegionData("VaultOfTheWarrior", 30, 31, "Travel: Vault of the Warrior", []),
    "TerramorphousPeak": Borderlands1RegionData("TerramorphousPeak", 30, 30, "Travel: Terramorphous Peak", [], story_req_regions=["VaultOfTheWarrior"], dlc_group="basegame_side"),

    "FFSIntroSanctuary": Borderlands1RegionData("FFSIntroSanctuary", 30, 30, "Travel: FFS Intro Sanctuary", ["Backburner"], dlc_group="ffs"),
    "Backburner": Borderlands1RegionData("Backburner", 30, 30, "Travel: The Backburner", ["DahlAbandon"], dlc_group="ffs"),
    "DahlAbandon": Borderlands1RegionData("DahlAbandon", 30, 30, "Travel: Dahl Abandon", ["Burrows", "HeliosFallen", "Mt.ScarabResearchCenter"], dlc_group="ffs"),
    "Burrows": Borderlands1RegionData("Burrows", 30, 30, "Travel: The Burrows", ["HeliosFallen", "WrithingDeep"], dlc_group="ffs"),
    "HeliosFallen": Borderlands1RegionData("HeliosFallen", 30, 30, "Travel: Helios Fallen", [], story_req_regions=["Burrows"], dlc_group="ffs"),
    "Mt.ScarabResearchCenter": Borderlands1RegionData("Mt.ScarabResearchCenter", 30, 30, "Travel: Mt. Scarab Research Center", ["FFSBossFight"], story_req_regions=["HeliosFallen"], dlc_group="ffs"),
    "FFSBossFight": Borderlands1RegionData("FFSBossFight", 30, 30, "Travel: FFS Boss Fight", [], dlc_group="ffs"),
    "WrithingDeep": Borderlands1RegionData("WrithingDeep", 30, 30, "Travel: Writhing Deep", [], story_req_regions=["FFSBossFight"], dlc_group="ffs"),

    "UnassumingDocks": Borderlands1RegionData("UnassumingDocks", 30, 30, "Travel: Unassuming Docks", ["FlamerockRefuge"], dlc_group="tina"),
    "FlamerockRefuge": Borderlands1RegionData("FlamerockRefuge", 30, 30, "Travel: Flamerock Refuge", ["Forest", "MurderlinsTemple"], dlc_group="tina"),
    "Forest": Borderlands1RegionData("Forest", 30, 30, "Travel: The Forest", ["ImmortalWoods"], dlc_group="tina"),
    "ImmortalWoods": Borderlands1RegionData("ImmortalWoods", 30, 30, "Travel: Immortal Woods", ["MinesOfAvarice"], dlc_group="tina"),
    "MinesOfAvarice": Borderlands1RegionData("MinesOfAvarice", 30, 30, "Travel: Mines of Avarice", ["HatredsShadow"], dlc_group="tina"),
    "HatredsShadow": Borderlands1RegionData("HatredsShadow", 30, 30, "Travel: Hatred's Shadow", ["LairOfInfiniteAgony"], dlc_group="tina"),
    "LairOfInfiniteAgony": Borderlands1RegionData("LairOfInfiniteAgony", 30, 30, "Travel: Lair of Infinite Agony", ["DragonKeep", "WingedStorm"], dlc_group="tina"),
    "DragonKeep": Borderlands1RegionData("DragonKeep", 30, 30, "Travel: Dragon Keep", [], dlc_group="tina"),
    "MurderlinsTemple": Borderlands1RegionData("MurderlinsTemple", 30, 30, "Travel: Murderlin's Temple", [], story_req_regions=["DragonKeep"], dlc_group="tina"),
    "WingedStorm": Borderlands1RegionData("WingedStorm", 30, 30, "Travel: The Winged Storm", [], story_req_regions=["DragonKeep"], dlc_group="tina"),

    "BadassCrater": Borderlands1RegionData("BadassCrater", 15, 16, "Travel: Badass Crater", ["Beatdown", "TorgueArena", "BadassCraterBar", "SouthernRaceway", "Forge"], dlc_group="torgue"),
    "TorgueArena": Borderlands1RegionData("TorgueArena", 15, 17, "Travel: Torgue Arena", [], dlc_group="torgue"),
    "Beatdown": Borderlands1RegionData("Beatdown", 15, 18, "Travel: The Beatdown", ["PyroPetesBar"], story_req_regions=["TorgueArena"], dlc_group="torgue"),
    "PyroPetesBar": Borderlands1RegionData("PyroPetesBar", 15, 18, "Travel: Pyro Pete's Bar", [], dlc_group="torgue"),
    "BadassCraterBar": Borderlands1RegionData("BadassCraterBar", 15, 15, "Travel: Badass Crater Bar", [], story_req_regions=["PyroPetesBar"], dlc_group="torgue"),
    "SouthernRaceway": Borderlands1RegionData("SouthernRaceway", 15, 19, "Travel: Southern Raceway", [], story_req_regions=["BadassCraterBar"], dlc_group="torgue"),
    "Forge": Borderlands1RegionData("Forge", 15, 20, "Travel: The Forge", [], story_req_regions=["SouthernRaceway"], dlc_group="torgue"),

    "Oasis": Borderlands1RegionData("Oasis", 15, 16, "Travel: Oasis", ["Wurmwater", "HaytersFolly", "LeviathansLair"], dlc_group="scarlett"),
    "Wurmwater": Borderlands1RegionData("Wurmwater", 15, 17, "Travel: Wurmwater", ["WashburneRefinery", "Rustyards", "MagnysLighthouse"], dlc_group="scarlett"),
    "HaytersFolly": Borderlands1RegionData("HaytersFolly", 15, 18, "Travel: Hayter's Folly", [], story_req_regions=["Wurmwater"], dlc_group="scarlett"),
    "Rustyards": Borderlands1RegionData("Rustyards", 15, 18, "Travel: The Rustyards", [], story_req_regions=["HaytersFolly"], dlc_group="scarlett"),
    "WashburneRefinery": Borderlands1RegionData("WashburneRefinery", 15, 18, "Travel: Washburne Refinery", [], story_req_regions=["Rustyards"], dlc_group="scarlett"),
    "MagnysLighthouse": Borderlands1RegionData("MagnysLighthouse", 15, 19, "Travel: Magnys Lighthouse", [], story_req_regions=["WashburneRefinery"], dlc_group="scarlett"),
    "LeviathansLair": Borderlands1RegionData("LeviathansLair", 15, 19, "Travel: The Leviathan's Lair", [], story_req_regions=["MagnysLighthouse"], dlc_group="scarlett"),

    "HuntersGrotto": Borderlands1RegionData("HuntersGrotto", 30, 30, "Travel: Hunter's Grotto", ["ScyllasGrove", "CandlerakksCrag", "ArdortonStation"], dlc_group="hammerlock"),
    "ScyllasGrove": Borderlands1RegionData("ScyllasGrove", 30, 30, "Travel: Scylla's Grove", ["ArdortonStation"], dlc_group="hammerlock"),
    "ArdortonStation": Borderlands1RegionData("ArdortonStation", 30, 30, "Travel: Ardorton Station", [], story_req_regions=["ScyllasGrove"], dlc_group="hammerlock"),
    "CandlerakksCrag": Borderlands1RegionData("CandlerakksCrag", 30, 30, "Travel: Candlerakk's Cragg", ["Terminus"], story_req_regions=["ArdortonStation"], dlc_group="hammerlock"),
    "Terminus": Borderlands1RegionData("Terminus", 30, 30, "Travel: Terminus", [], dlc_group="hammerlock"),

    "DigistructPeak": Borderlands1RegionData("DigistructPeak", 0, 3, "Travel: Digistruct Peak", ["DigistructPeakInner"], dlc_group="digi"),
    "DigistructPeakInner": Borderlands1RegionData("DigistructPeakInner", 30, 30, "Travel: Digistruct Peak", [], dlc_group="digi"),
    # "DigistructPeakOP5": Borderlands1RegionData("DigistructPeakOP5", "", []),

    "HallowedHollow": Borderlands1RegionData("HallowedHollow", 15, 17, "Travel: Hallowed Hollow", [], dlc_group="headhunter"),
    "GluttonyGulch": Borderlands1RegionData("GluttonyGulch", 15, 17, "Travel: Gluttony Gulch", [], dlc_group="headhunter"),
    "MarcusMercenaryShop": Borderlands1RegionData("MarcusMercenaryShop", 15, 17, "Travel: Marcus's Mercenary Shop", [], dlc_group="headhunter"),
    "RotgutDistillery": Borderlands1RegionData("RotgutDistillery", 15, 17, "Travel: Rotgut Distillery", [], dlc_group="headhunter"),
    "WamBamIsland": Borderlands1RegionData("WamBamIsland", 15, 17, "Travel: Wam Bam Island", [], dlc_group="headhunter"),
}

progressive_travel_dict = {
    "basegame": [r for r in region_data_table if region_data_table[r].dlc_group == "basegame"],
    "basegame_side": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "basegame_side"],
    "ffs": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "ffs"],
    "tina": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "tina"],
    "torgue": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "torgue"],
    "scarlett": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "scarlett"],
    "hammerlock": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "hammerlock"],
    "headhunter": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "headhunter"],
}

progressive_travel_items = {
    "basegame": "Progressive Travel: Base Game",
    "basegame_side": "Progressive Travel: Side Area",
    "ffs": "Progressive Travel: Fight For Sanctuary DLC",
    "tina": "Progressive Travel: Tina DLC",
    "torgue": "Progressive Travel: Torgue DLC",
    "scarlett": "Progressive Travel: Scarlett DLC",
    "hammerlock": "Progressive Travel: Hammerlock DLC",
    "headhunter": "Progressive Travel: Headhunters",
}
