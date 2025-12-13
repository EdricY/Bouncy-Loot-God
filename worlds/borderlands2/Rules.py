from worlds.generic.Rules import set_rule, add_rule

from . import Borderlands2World
from .Regions import region_data_table
from .Locations import Borderlands2Location
from .Items import Borderlands2Item
from BaseClasses import ItemClassification


def set_rules(world: Borderlands2World):

    # items must be classified as progression to use in rules here
    add_rule(world.multiworld.get_entrance("WindshearWaste to SouthernShelf", world.player),
        lambda state: state.has("Melee", world.player) and state.has("Common Pistol", world.player))
    #add_rule(world.multiworld.get
    # add_rule(world.multiworld.get_entrance("SouthernShelf to ThreeHornsDivide", world.player),
    #     lambda state: state.has("Common Pistol", world.player))
    # add_rule(world.multiworld.get_location("Enemy WindshearWaste: Knuckle Dragger", world.player),
    #     lambda state: state.has("Melee", world.player))
    add_rule(world.multiworld.get_location("Symbol Opportunity: Construction Site", world.player),
             lambda state: state.has("Crouch", world.player))



    # ensure you can at least jump a little before wildlife preserve
    if world.options.jump_checks.value > 0:
        add_rule(world.multiworld.get_entrance("Highlands to WildlifeExploitationPreserve", world.player),
            lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_entrance("BadassCrater to TorgueArena", world.player),
            lambda state: state.has("Progressive Jump", world.player))
        #add_rule(world.multiworld.get_region("Oasis", world.player),
        #         lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Vending Tundra Farm: Guns", world.player),
                 lambda state: state.has("Progressive Jump", world.player))

        #Quests that need jump
        add_rule(world.multiworld.get_location("Quest ThreeHornsValley: No Vacancy", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Quest ThreeHornsValley: Neither Rain nor Sleet nor Skags", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Quest Dust: Too Close For Missiles", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Quest Tundra Express: Mine, All Mine", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Quest Tundra Express: The Pretty Good Train Robbery", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Quest Highlands: Hidden Journals", world.player),
                 lambda state: state.has("Progressive Jump", world.player))

        #Enemies that need jump
        add_rule(world.multiworld.get_location("Enemy BloodshotStronghold: Flinter", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Enemy TundraExpress: Prospector Zeke", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Enemy CausticCaverns: Badass Creeper", world.player),
                 lambda state: state.has("Progressive Jump", world.player) and state.has("Melee", world.player))


        #Vault Symbols needing jump
        add_rule(world.multiworld.get_location("Symbol SouthernShelfBay: Ice Flows Shipwreck", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol SouthernShelf: Flynt's Ship", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol SouthernShelf: Safehouse", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol ThreeHornsDivide: Billboard", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol Sanctuary: Rooftop", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol Sanctuary: Parkour Door", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol Southpaw: Parkour", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol Southpaw: Engine", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol ThreeHornsValley: Frostsprings Wall", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol Dust: Moonshiner Lid", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol Bloodshot: Switch Room", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol Fridge: Secret Stash", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol Fridge: Sheetmetal Roof", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol ThousandCuts: No Man's Land Shack", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol Lynchwood: Gunslinger Roof", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol Lynchwood: Main Street", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol Opportunity: Office Bridge", world.player),
                 lambda state: state.has("Progressive Jump", world.player))
        add_rule(world.multiworld.get_location("Symbol BadassCrater: Billboard Lower", world.player),
                 lambda state: state.has("Progressive Jump", world.player))

    #need melee to break vines to Hector
    add_rule(world.multiworld.get_entrance("Mt.ScarabResearchCenter to FFSBossFight", world.player),
             lambda state: state.has("Melee", world.player))
    #ensure you can crouch for these checks
    add_rule(world.multiworld.get_entrance("CandlerakksCragg to Terminus", world.player),
            lambda state: state.has("Crouch", world.player))
    #need crouch for this vault symbol
    add_rule(world.multiworld.get_location("Symbol Opportunity: Construction Site", world.player),
             lambda state: state.has("Crouch", world.player))

    # for loc in locs_with_jump_req:
    #     add_rule(world.multiworld.get_location(loc, world.player),
    #     lambda state: state.has("Progressive Jump", world.player))


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
                add_rule(world.multiworld.get_entrance(exit_name, world.player),
                     lambda state, travel_item=t_item: state.has(travel_item, world.player))
            elif t_item and isinstance(t_item, list):
                add_rule(world.multiworld.get_entrance(exit_name, world.player),
                     lambda state, travel_item=t_item: state.has_all(travel_item, world.player))


