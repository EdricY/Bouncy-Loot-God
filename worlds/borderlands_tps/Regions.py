from typing import Dict, List, NamedTuple, Union


class BorderlandsTPSRegionData(NamedTuple):
    name: str = ""
    min_level: int = 0 # the lowest level you could begin farming exp in this area
    max_level: int = 0 # the highest expected level you could farm exp in this area up to
    travel_item_name: str = ""
    connecting_regions: List[str] = []
    story_req_regions: List[str] = []
    dlc_group: str = "basegame"

region_data_table: Dict[str, BorderlandsTPSRegionData] = {
    "Menu": BorderlandsTPSRegionData("Menu", 0, 0, "", [
        "Helios Station",
        "Abandoned Training Facility",
        "The Holodome",
        "Deck 13 ½",
    ], dlc_group= "menu"),
    "Helios Station":                BorderlandsTPSRegionData("Helios Station", 0, 3, "", ["Serenity's Waste"]),
    "Serenity's Waste":              BorderlandsTPSRegionData("Serenity's Waste", 2, 7, "Travel: Serenity's Waste", ["Regolith Range", "Concordia"]),
    "Regolith Range":                BorderlandsTPSRegionData("Regolith Range", 3, 10, "Travel: Regolith Range", [], story_req_regions=["Serenity's Waste"]),
    "Concordia":                     BorderlandsTPSRegionData("Concordia", 5, 12, "Travel: Concordia", ["Triton Flats", "The Meriff's Office", "Hyperion Hub of Heroism"], story_req_regions=["Serenity's Waste", "Regolith Range"]),
    "Triton Flats":                  BorderlandsTPSRegionData("Triton Flats", 5, 15, "Travel: Triton Flats", ["Stanton's Liver", "Outlands Canyon", "Titan Industrial Facility", "Crisis Scar", "Vorago Solitude"]),
    "Crisis Scar":                   BorderlandsTPSRegionData("Crisis Scar", 5, 15, "Travel: Crisis Scar", []),
    "The Meriff's Office":           BorderlandsTPSRegionData("The Meriff's Office", 7, 15, "Travel: The Meriff's Office", [], story_req_regions=["Crisis Scar"]),
    "Stanton's Liver":               BorderlandsTPSRegionData("Stanton's Liver", 8, 8, "Travel: Stanton's Liver", [], dlc_group="basegame_side"),
    "Outlands Canyon":               BorderlandsTPSRegionData("Outlands Canyon", 9, 15, "Travel: Outlands Canyon", ["Outlands Spur", "Abandoned Training Facility"], story_req_regions=["The Meriff's Office"]),
    "Outlands Spur":                 BorderlandsTPSRegionData("Outlands Spur", 10, 20, "Travel: Outlands Spur", ["Pity's Fall"]),
    "Pity's Fall":                   BorderlandsTPSRegionData("Pity's Fall", 11, 20, "Travel: Pity's Fall", []),
    "Titan Industrial Facility":     BorderlandsTPSRegionData("Titan Industrial Facility", 12, 20, "Travel: Titan Industrial Facility", ["Titan Robot Production Plant", "Sub-Level 13"]),
    "Sub-Level 13":                  BorderlandsTPSRegionData("Sub-Level 13", 14, 16, "Travel: Sub-Level 13", [], dlc_group="basegame_side", story_req_regions=["Titan Robot Production Plant"]),
    "Titan Robot Production Plant":  BorderlandsTPSRegionData("Titan Robot Production Plant", 13, 20, "Travel: Titan Robot Production Plant", []),
    "Hyperion Hub of Heroism":       BorderlandsTPSRegionData("Hyperion Hub of Heroism", 15, 25, "Travel: Hyperion Hub of Heroism", ["Jack's Office", "Research and Development", "Veins of Helios"], story_req_regions=["Titan Robot Production Plant"]),
    "Jack's Office":                 BorderlandsTPSRegionData("Jack's Office", 15, 25, "Travel: Jack's Office", []),
    "Research and Development":      BorderlandsTPSRegionData("Research and Development", 16, 25, "Travel: Research and Development", [], story_req_regions=["Jack's Office"]),
    "Veins of Helios":               BorderlandsTPSRegionData("Veins of Helios", 17, 25, "Travel: Veins of Helios", ["Lunar Launching Station"]),
    "Lunar Launching Station":       BorderlandsTPSRegionData("Lunar Launching Station", 18, 25, "Travel: Lunar Launching Station", ["Eye of Helios"]),
    "Eye of Helios":                 BorderlandsTPSRegionData("Eye of Helios", 18, 25, "Travel: Eye of Helios", []),
    "Vorago Solitude":               BorderlandsTPSRegionData("Vorago Solitude", 18, 30, "Travel: Vorago Solitude", ["Outfall Pumping Station"], story_req_regions=["Hyperion Hub of Heroism"]),
    "Outfall Pumping Station":       BorderlandsTPSRegionData("Outfall Pumping Station", 19, 30, "Travel: Outfall Pumping Station", ["Tycho's Ribs"]),
    "Tycho's Ribs":                  BorderlandsTPSRegionData("Tycho's Ribs", 19, 30, "Travel: Tycho's Ribs", ["Eleseer"]),
    "Eleseer":                       BorderlandsTPSRegionData("Eleseer", 20, 30, "Travel: Eleseer", []),
    "Abandoned Training Facility":   BorderlandsTPSRegionData("Abandoned Training Facility", 25, 30, "Travel: Abandoned Training Facility", [], dlc_group="shock_drop"),
    "The Holodome":                  BorderlandsTPSRegionData("The Holodome", 25, 30, "Travel: The Holodome", [], dlc_group="holodome", story_req_regions=["Tycho's Ribs"]),
    "Deck 13 ½":                     BorderlandsTPSRegionData("Deck 13 ½", 25, 30, "Travel: Deck 13 ½", ["The Nexus"], dlc_group="claptrap", story_req_regions=["Tycho's Ribs"]),
    "The Nexus":                     BorderlandsTPSRegionData("The Nexus", 25, 30, "Travel: The Nexus", ["Motherlessboard", "Subconscious"], dlc_group="claptrap"),
    "Motherlessboard":               BorderlandsTPSRegionData("Motherlessboard", 25, 30, "Travel: Motherlessboard", ["Cluster 00773 P4ND0R4", "Cluster 99002 0V3RL00K"], dlc_group="claptrap"),
    "Cluster 00773 P4ND0R4":         BorderlandsTPSRegionData("Cluster 00773 P4ND0R4", 25, 30, "Travel: Cluster 00773 P4ND0R4", [], dlc_group="claptrap"),
    "Cluster 99002 0V3RL00K":        BorderlandsTPSRegionData("Cluster 99002 0V3RL00K", 25, 30, "Travel: Cluster 99002 0V3RL00K", [], dlc_group="claptrap"),
    "Subconscious":                  BorderlandsTPSRegionData("Subconscious", 25, 30, "Travel: Subconscious", ["The Cortex"], dlc_group="claptrap"),
    "The Cortex":                    BorderlandsTPSRegionData("The Cortex", 25, 30, "Travel: The Cortex", ["EOSArena"], dlc_group="claptrap"),
    "EOSArena":                     BorderlandsTPSRegionData("EOSArena", 25, 30, "Travel: EOSArena", [], dlc_group="claptrap"),
}

progressive_travel_dict = {
    "basegame": [r for r in region_data_table if region_data_table[r].dlc_group == "basegame"],
    "basegame_side": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "basegame_side"],
    "shock_drop": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "shock_drop"],
    "holodome": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "holodome"],
    "claptrap": [""] + [r for r in region_data_table if region_data_table[r].dlc_group == "claptrap"],
}

progressive_travel_items = {
    "basegame": "Progressive Travel: Base Game",
    "basegame_side": "Progressive Travel: Side Area",
    "claptrap": "Progressive Travel: Claptastic Voyage DLC",
    "shock_drop": "Progressive Travel: Shock Drop Slaughter Pit DLC", #there is only one travel item here 
    "holodome": "Progressive Travel: The Holodome Onslaught DLC", #there is only one travel item here 
}