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
    # add_rule(world.multiworld.get_entrance("SouthernShelf to ThreeHornsDivide", world.player),
    #     lambda state: state.has("Common Pistol", world.player))
    # add_rule(world.multiworld.get_location("Enemy WindshearWaste: Knuckle Dragger", world.player),
    #     lambda state: state.has("Melee", world.player))

    # ensure you can at least jump a little before wildlife preserve
    add_rule(world.multiworld.get_entrance("Highlands to WildlifeExploitationPreserve", world.player),
        lambda state: state.has("Progressive Jump", world.player))


    if world.options.entrance_locks.value == 0:
        # skip if no entrance locks
        return

    for name, region_data in region_data_table.items():
        region = world.multiworld.get_region(name, world.player)
        for c_region_name in region_data.connecting_regions:
            c_region_data = region_data_table[c_region_name]
            exit_name = f"{region.name} to {c_region_name}"
            if c_region_data.travel_item_name:
                add_rule(world.multiworld.get_entrance(exit_name, world.player),
                     lambda state, travel_item=c_region_data.travel_item_name: state.has(travel_item, world.player))
                exit_name = f"{region.name} to {c_region_name}"

