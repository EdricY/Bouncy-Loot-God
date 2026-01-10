from typing import Dict, List, NamedTuple, Union


class Borderlands2RegionData(NamedTuple):
    name: str = ""
    level_req: int = 0
    travel_item_name: Union[str, List[str]] = ""
    connecting_regions: List[str] = []
    @property
    def primary_travel_item(self):
        if type(self.travel_item_name) is str:
            return self.travel_item_name
        elif len(self.travel_item_name) > 0:
            return self.travel_item_name[0]
        return ""

region_data_table: Dict[str, Borderlands2RegionData] = {
    "Menu": Borderlands2RegionData("Menu", 0, "", [
        "WindshearWaste",
        "DigistructPeak",
        # "FFSIntroSanctuary",
        # "UnassumingDocks",
        # "BadassCrater",
        # "Oasis",
        # "HuntersGrotto",
        # "MarcusMercenaryShop",
        # "GluttonyGulch",
        # "RotgutDistillery",
        # "WamBamIsland",
        # "HallowedHollow",
    ]),

    "WindshearWaste": Borderlands2RegionData("WindshearWaste", 1, "", ["SouthernShelf"]),
    "SouthernShelf": Borderlands2RegionData("SouthernShelf", 3, "Travel: Southern Shelf", ["SouthernShelfBay", "ThreeHornsDivide"]),
    "SouthernShelfBay": Borderlands2RegionData("SouthernShelfBay", 4, "Travel: Southern Shelf Bay", []),
    "ThreeHornsDivide": Borderlands2RegionData("ThreeHornsDivide", 7, "Travel: Three Horns Divide", ["ThreeHornsValley", "Sanctuary"]),
    "ThreeHornsValley": Borderlands2RegionData("ThreeHornsValley", 8, "Travel: Three Horns Valley", ["SouthpawSteam&Power", "Dust"]),
    "Sanctuary": Borderlands2RegionData("Sanctuary", 7, "Travel: Sanctuary", ["FrostburnCanyon"]),
    "FrostburnCanyon": Borderlands2RegionData("FrostburnCanyon", 9, "Travel: Frostburn Canyon", ["BloodshotStronghold", "FriendshipGulag"]),
    "SouthpawSteam&Power": Borderlands2RegionData("SouthpawSteam&Power", 8, "Travel: Southpaw Steam & Power", []),
    "Dust": Borderlands2RegionData("Dust", 15, "Travel: The Dust", ["Lynchwood"]),
    "BloodshotStronghold": Borderlands2RegionData("BloodshotStronghold", 12, ["Travel: Bloodshot Stronghold", "Travel: The Dust", "Travel: Frostburn Canyon", "Travel: Three Horns Valley"], ["BloodshotRamparts"]),
    "BloodshotRamparts": Borderlands2RegionData("BloodshotRamparts", 12, "Travel: Bloodshot Ramparts", [
        "TundraExpress",
        "MarcusMercenaryShop",
        "GluttonyGulch",
        "RotgutDistillery",
        "WamBamIsland",
        "HallowedHollow",
        "BadassCrater",
        "Oasis",
    ]),
    "Fridge": Borderlands2RegionData("Fridge", 15, ["Travel: The Fridge"], ["FinksSlaughterhouse", "HighlandsOutwash"]),
    "HighlandsOutwash": Borderlands2RegionData("HighlandsOutwash", 15, ["Travel: Highlands Outwash"], ["Highlands"]),
    "Highlands": Borderlands2RegionData("Highlands", 16, ["Travel: Highlands"], ["HolySpirits", "WildlifeExploitationPreserve", "ThousandCuts","Opportunity"]),
    "FriendshipGulag": Borderlands2RegionData("FriendshipGulag", 10, ["Travel: Friendship Gulag"], []),
    "Lynchwood": Borderlands2RegionData("Lynchwood", 24, ["Travel: Lynchwood"], []),
    "FinksSlaughterhouse": Borderlands2RegionData("FinksSlaughterhouse", 15, ["Travel: Fink's Slaughterhouse"], []),
    "SanctuaryHole": Borderlands2RegionData("SanctuaryHole", 13, ["Travel: Sanctuary Hole"], ["CausticCaverns"]),
    "TerramorphousPeak": Borderlands2RegionData("TerramorphousPeak", 30, ["Travel: Terramorphous Peak"], []),
    "CausticCaverns": Borderlands2RegionData("CausticCaverns", 16, ["Travel: Caustic Caverns"], []),
    "Opportunity": Borderlands2RegionData("Opportunity", 20, ["Travel: Opportunity"], ["Bunker"]),
    "HolySpirits": Borderlands2RegionData("HolySpirits", 18, ["Travel: The Holy Spirits"], []),
    "WildlifeExploitationPreserve": Borderlands2RegionData("WildlifeExploitationPreserve", 19, ["Travel: Wildlife Exploitation Preserve"], ["NaturalSelectionAnnex", "Bunker"]),
    "NaturalSelectionAnnex": Borderlands2RegionData("NaturalSelectionAnnex", 20, ["Travel: Natural Selection Annex"], []),
    "TundraExpress": Borderlands2RegionData("TundraExpress", 13, ["Travel: Tundra Express"], ["EndOfTheLine"]),
    "EndOfTheLine": Borderlands2RegionData("EndOfTheLine", 13, ["Travel: End of the Line"], ["SanctuaryHole", "Fridge"]),
    "Bunker": Borderlands2RegionData("Bunker", ["Travel: The Bunker",
                                                "Travel: Wildlife Exploitation Preserve",
                                                "Travel: Thousand Cuts",
                                                "Travel: Opportunity"], ["ControlCoreAngel"]),
    "ThousandCuts": Borderlands2RegionData("ThousandCuts", 20, ["Travel: Thousand Cuts"], ["Bunker"]),
    "EridiumBlight": Borderlands2RegionData("EridiumBlight", 25, ["Travel: Eridium Blight"], ["OreChasm", "SawtoothCauldron"]),
    "SawtoothCauldron": Borderlands2RegionData("SawtoothCauldron", 25, ["Travel: Sawtooth Cauldron"], ["AridNexusBoneyard"]),
    "OreChasm": Borderlands2RegionData("OreChasm", 25, ["Travel: Ore Chasm"], []),
    "ControlCoreAngel": Borderlands2RegionData("ControlCoreAngel", 25, ["Travel: Control Core Angel"], ["EridiumBlight"]),
    "AridNexusBoneyard": Borderlands2RegionData("AridNexusBoneyard", 26, ["Travel: Arid Nexus Boneyard"], ["AridNexusBadlands"]),
    "AridNexusBadlands": Borderlands2RegionData("AridNexusBadlands", 26, ["Travel: Arid Nexus Badlands"], ["HerosPass"]),
    "HerosPass": Borderlands2RegionData("HerosPass", 29, ["Travel: Hero's Pass"], ["VaultOfTheWarrior"]),
    "VaultOfTheWarrior": Borderlands2RegionData("VaultOfTheWarrior", 30, ["Travel: Vault of the Warrior"], ["TerramorphousPeak",
        "FFSIntroSanctuary",
        "UnassumingDocks",
        "HuntersGrotto",
        "DigistructPeakInner",
    ]),

    "FFSIntroSanctuary": Borderlands2RegionData("FFSIntroSanctuary", 30, ["Travel: FFS Intro Sanctuary"], ["Backburner"]),
    "Burrows": Borderlands2RegionData("Burrows", 30, ["Travel: The Burrows"], ["HeliosFallen"]),
    "Backburner": Borderlands2RegionData("Backburner", 30, ["Travel: The Backburner", "Travel: FFS Intro Sanctuary"], ["DahlAbandon"]),
    "DahlAbandon": Borderlands2RegionData("DahlAbandon", 30, ["Travel: Dahl Abandon"], ["Burrows"]),
    "HeliosFallen": Borderlands2RegionData("HeliosFallen", 30, ["Travel: Helios Fallen"], ["Mt.ScarabResearchCenter"]),
    "WrithingDeep": Borderlands2RegionData("WrithingDeep", 30, ["Travel: Writhing Deep"], []),
    "Mt.ScarabResearchCenter": Borderlands2RegionData("Mt.ScarabResearchCenter", 30, ["Travel: Mt. Scarab Research Center"], ["FFSBossFight"]),
    "FFSBossFight": Borderlands2RegionData("FFSBossFight", 30, ["Travel: FFS Boss Fight"], ["WrithingDeep"]),

    "UnassumingDocks": Borderlands2RegionData("UnassumingDocks", 30, ["Travel: Unassuming Docks"], ["FlamerockRefuge"]),
    "FlamerockRefuge": Borderlands2RegionData("FlamerockRefuge", 30, ["Travel: Flamerock Refuge"], ["Forest"]),
    "HatredsShadow": Borderlands2RegionData("HatredsShadow", 30, ["Travel: Hatred's Shadow"], ["LairOfInfiniteAgony"]),
    "LairOfInfiniteAgony": Borderlands2RegionData("LairOfInfiniteAgony", 30, ["Travel: Lair of Infinite Agony"], ["DragonKeep"]),
    "ImmortalWoods": Borderlands2RegionData("ImmortalWoods", 30, ["Travel: Immortal Woods"], ["MinesOfAvarice"]),
    "Forest": Borderlands2RegionData("Forest", 30, ["Travel: The Forest"], ["ImmortalWoods"]),
    "MinesOfAvarice": Borderlands2RegionData("MinesOfAvarice", 30, ["Travel: Mines of Avarice"], ["HatredsShadow"]),
    "MurderlinsTemple": Borderlands2RegionData("MurderlinsTemple", 30, ["Travel: Murderlin's Temple"], []),
    "WingedStorm": Borderlands2RegionData("WingedStorm", 30, ["Travel: The Winged Storm"], []),
    "DragonKeep": Borderlands2RegionData("DragonKeep", 30, ["Travel: Dragon Keep"], ["WingedStorm", "MurderlinsTemple"]),

    "BadassCrater": Borderlands2RegionData("BadassCrater", 15, ["Travel: Badass Crater"], ["TorgueArena"]),
    "Beatdown": Borderlands2RegionData("Beatdown", 15, ["Travel: The Beatdown"], ["PyroPetesBar"]),
    "TorgueArena": Borderlands2RegionData("TorgueArena", 15, ["Travel: Torgue Arena"], ["TorgueArenaRing","Beatdown"]),
    "TorgueArenaRing": Borderlands2RegionData("TorgueArenaRing", 15, ["Travel: Torgue Arena Ring"], ["SouthernRaceway"]),
    "BadassCraterBar": Borderlands2RegionData("BadassCraterBar", 15, ["Travel: Badass Crater Bar"], ["SouthernRaceway"]),
    "Forge": Borderlands2RegionData("Forge", 15, ["Travel: The Forge"], []),
    "SouthernRaceway": Borderlands2RegionData("SouthernRaceway", 15, ["Travel: Southern Raceway", "Travel: Torgue Arena Ring"], ["Forge"]),
    "PyroPetesBar": Borderlands2RegionData("PyroPetesBar", 15, ["Travel: Pyro Pete's Bar"], ["BadassCraterBar"]),

    "Oasis": Borderlands2RegionData("Oasis", 15, ["Travel: Oasis"], ["Wurmwater"]),
    "HaytersFolly": Borderlands2RegionData("HaytersFolly", 15, ["Travel: Hayter's Folly"], ["Rustyards"]),
    "Wurmwater": Borderlands2RegionData("Wurmwater", 15, ["Travel: Wurmwater"], ["HaytersFolly"]),
    "WashburneRefinery": Borderlands2RegionData("WashburneRefinery", 15, ["Travel: Washburne Refinery"], ["MagnysLighthouse"]),
    "Rustyards": Borderlands2RegionData("Rustyards", 15, ["Travel: The Rustyards"], ["WashburneRefinery"]),
    "MagnysLighthouse": Borderlands2RegionData("MagnysLighthouse", 15, ["Travel: Magnys Lighthouse"], ["LeviathansLair"]),
    "LeviathansLair": Borderlands2RegionData("LeviathansLair", 15, ["Travel: The Leviathan's Lair"], []),

    "HuntersGrotto": Borderlands2RegionData("HuntersGrotto", 30, ["Travel: Hunter's Grotto"], ["ScyllasGrove"]),
    "CandlerakksCrag": Borderlands2RegionData("CandlerakksCrag", 30, ["Travel: Candlerakk's Cragg"], ["Terminus"]),
    "ArdortonStation": Borderlands2RegionData("ArdortonStation", 30, ["Travel: Ardorton Station"], ["CandlerakksCrag"]),
    "ScyllasGrove": Borderlands2RegionData("ScyllasGrove", 30, ["Travel: Scylla's Grove"], ["ArdortonStation"]),
    "Terminus": Borderlands2RegionData("Terminus", 30, ["Travel: Terminus"], []),

    "DigistructPeak": Borderlands2RegionData("DigistructPeak", 0, ["Travel: Digistruct Peak"], []),
    "DigistructPeakInner": Borderlands2RegionData("DigistructPeakInner", 30, ["Travel: Digistruct Peak"], []),
    # "DigistructPeakOP5": Borderlands2RegionData("DigistructPeakOP5", "", []),

    "MarcusMercenaryShop": Borderlands2RegionData("MarcusMercenaryShop", 15, ["Travel: Marcus's Mercenary Shop"], []),
    "GluttonyGulch": Borderlands2RegionData("GluttonyGulch", 15, ["Travel: Gluttony Gulch"], []),
    "RotgutDistillery": Borderlands2RegionData("RotgutDistillery", 15, ["Travel: Rotgut Distillery"], []),
    "WamBamIsland": Borderlands2RegionData("WamBamIsland", 15, ["Travel: Wam Bam Island"], []),
    "HallowedHollow": Borderlands2RegionData("HallowedHollow", 15, ["Travel: Hallowed Hollow"], []),
}
