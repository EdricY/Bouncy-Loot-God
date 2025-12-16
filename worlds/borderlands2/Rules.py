from worlds.generic.Rules import set_rule, add_rule

from . import Borderlands2World
from .Regions import region_data_table
from .Locations import Borderlands2Location
from .Items import Borderlands2Item
from BaseClasses import ItemClassification

# TODO record and calculate how much jump is required
locs_with_jump_required = [
    "Vending Tundra Farm: Guns",
    "Quest ThreeHornsValley: No Vacancy",
    "Vending ThreeHornsValley Motel: Guns",
    "Vending ThreeHornsValley Motel: Zed's Meds",
    "Vending ThreeHornsValley Motel: Ammo Dump",
    "Quest ThreeHornsValley: Neither Rain nor Sleet nor Skags",
    "Quest Dust: Too Close For Missiles",
    "Quest Tundra Express: Mine, All Mine",
    "Quest Tundra Express: The Pretty Good Train Robbery",
    "Quest Highlands: Hidden Journals",
    "Enemy BloodshotStronghold: Flinter",
    "Enemy TundraExpress: Prospector Zeke",
    "Enemy CausticCaverns: Badass Creeper",
    "Symbol SouthernShelfBay: Ice Flows Shipwreck",
    "Symbol SouthernShelf: Flynt's Ship",
    "Symbol SouthernShelf: Safehouse",
    "Symbol ThreeHornsDivide: Billboard",
    "Symbol Sanctuary: Rooftop",
    "Symbol Sanctuary: Parkour Door",
    "Symbol Southpaw: Parkour",
    "Symbol Southpaw: Engine",
    "Symbol ThreeHornsValley: Frostsprings Wall",
    "Symbol Dust: Moonshiner Lid",
    "Symbol Bloodshot: Switch Room",
    "Symbol Fridge: Secret Stash",
    "Symbol Fridge: Sheetmetal Roof",
    "Symbol ThousandCuts: No Man's Land Shack",
    "Symbol Lynchwood: Gunslinger Roof",
    "Symbol Lynchwood: Main Street",
    "Symbol Opportunity: Office Bridge",
    "Symbol BadassCrater: Billboard Lower",
]

def try_add_rule(place, rule):
    if place is None:
        return
    try:
        add_rule(place, rule)
    except:
        print(f"failed setting rule at {place}")


def set_rules(world: Borderlands2World):

    # items must be classified as progression to use in rules here
    try_add_rule(world.try_get_entrance("WindshearWaste to SouthernShelf"),
        lambda state: state.has("Melee", world.player) and state.has("Common Pistol", world.player))
    #add_rule(world.multiworld.get
    # add_rule(world.multiworld.get_entrance("SouthernShelf to ThreeHornsDivide", world.player),
    #     lambda state: state.has("Common Pistol", world.player))
    # add_rule(world.multiworld.get_location("Enemy WindshearWaste: Knuckle Dragger", world.player),
    #     lambda state: state.has("Melee", world.player))
    try_add_rule(world.try_get_location("Symbol Opportunity: Construction Site"),
        lambda state: state.has("Crouch", world.player))

    if world.options.jump_checks.value > 0:
        # ensure you can at least jump a little before wildlife preserve
        try_add_rule(world.try_get_entrance("Highlands to WildlifeExploitationPreserve"),
            lambda state: state.has("Progressive Jump", world.player))
        try_add_rule(world.try_get_entrance("BadassCrater to TorgueArena"),
            lambda state: state.has("Progressive Jump", world.player))
        try_add_rule(world.try_get_entrance("BloodshotRamparts to Oasis"),
                 lambda state: state.has("Progressive Jump", world.player))

        for loc in locs_with_jump_required:
            try_add_rule(world.try_get_location(loc),
                lambda state: state.has("Progressive Jump", world.player)
            )

    #need melee to break vines to Hector
    try_add_rule(world.try_get_entrance("Mt.ScarabResearchCenter to FFSBossFight"),
             lambda state: state.has("Melee", world.player))
    #ensure you can crouch for these checks
    try_add_rule(world.try_get_entrance("CandlerakksCrag to Terminus"),
            lambda state: state.has("Crouch", world.player))
    #need crouch for this vault symbol
    try_add_rule(world.try_get_location("Symbol Opportunity: Construction Site"),
             lambda state: state.has("Crouch", world.player))

    if world.options.entrance_locks.value == 0:
        # skip if no entrance locks
        return

    for name, region_data in region_data_table.items():
        region = world.multiworld.get_region(name, world.player)
        for c_region_name in region_data.connecting_regions:
            c_region_data = region_data_table[c_region_name]
            exit_name = f"{region.name} to {c_region_name}"
            t_item = c_region_data.travel_item_name
            if t_item and isinstance(t_item, str):
                try_add_rule(world.try_get_entrance(exit_name),
                     lambda state, travel_item=t_item: state.has(travel_item, world.player))
            elif t_item and isinstance(t_item, list):
                try_add_rule(world.try_get_entrance(exit_name),
                     lambda state, travel_item=t_item: state.has_all(travel_item, world.player))


