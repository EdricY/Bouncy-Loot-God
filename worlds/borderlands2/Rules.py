from worlds.generic.Rules import set_rule, add_rule

from . import Borderlands2World
from .Regions import region_data_table
from .Locations import Borderlands2Location
from .Items import Borderlands2Item
from BaseClasses import ItemClassification


def set_rules(world: Borderlands2World):
    # entrances = []
    # entrance_item_names = []
    # for name, region_data in region_data_table.items():
    #     region = world.multiworld.get_region(name, world.player)
    #     for c_region_name in region_data.connecting_regions:
    #         c_region_data = region_data_table[c_region_name]
    #         exit_name = f"{region.name} to {c_region_name}"
    #         if c_region_data.travel_item_name:
    #             entrances.append(exit_name)
    #             entrance_item_names.append(c_region_data.travel_item_name)
    #
    # for i in range(len(entrances)):
    #     e = entrances[i]
    #     n = entrance_item_names[i]
    #     add_rule(world.multiworld.get_entrance(e, world.player),
    #          lambda state: state.has(n, world.player))




    for name, region_data in region_data_table.items():
        region = world.multiworld.get_region(name, world.player)
        for c_region_name in region_data.connecting_regions:
            c_region_data = region_data_table[c_region_name]
            exit_name = f"{region.name} to {c_region_name}"
            if c_region_data.travel_item_name:
                add_rule(world.multiworld.get_entrance(exit_name, world.player),
                     lambda state, travel_item=c_region_data.travel_item_name: state.has(travel_item, world.player))
                exit_name = f"{region.name} to {c_region_name}"
                print(exit_name + " " + c_region_data.travel_item_name)
            else:
                print("NO Travel Requirement" + exit_name)



    # add_rule(world.multiworld.get_entrance("SouthernShelf to ThreeHornsDivide", world.player),
    #      lambda state: state.has("Travel: Three Horns Divide", world.player))
    # add_rule(world.multiworld.get_entrance("ThreeHornsValley to Dust", world.player),
    #      lambda state: state.has("Travel: The Dust", world.player))
    # add_rule(world.multiworld.get_entrance("WindshearWaste to SouthernShelf", world.player),
    #      lambda state: state.has("Travel: Southern Shelf", world.player))

    # set_rule(world.multiworld.get_entrance("SouthernShelf to SouthernShelfBay", world.player),
    #          lambda state: state.has("Travel: Southern Shelf Bay", world.player))
    # set_rule(world.multiworld.get_entrance("SouthernShelfBay to SouthernShelf", world.player),
    #          lambda state: state.has("Travel: Southern Shelf", world.player))



    print('set_rules')
    # set_rule(world.multiworld.get_location("strawberry_17", world.player),
    #          lambda state: state.has_all({"dash_refill",
    #                                       "double_dash_refill",
    #                                       "feather",
    #                                       "traffic_block"}, world.player))
    # set_rule(world.multiworld.get_location("strawberry_18", world.player),
    #          lambda state: state.has("double_dash_refill", world.player))
    # set_rule(world.multiworld.get_location("strawberry_19", world.player),
    #          lambda state: state.has_all({"double_dash_refill",
    #                                       "spring"}, world.player))
    # set_rule(world.multiworld.get_location("strawberry_20", world.player),
    #          lambda state: state.has_all({"dash_refill",
    #                                       "feather",
    #                                       "breakables"}, world.player))
    #
    # set_rule(world.multiworld.get_location("strawberry_21", world.player),
    #          lambda state: state.has_all({"cassette",
    #                                       "traffic_block",
    #                                       "breakables"}, world.player))
    # set_rule(world.multiworld.get_location("strawberry_22", world.player),
    #          lambda state: state.has_all({"cassette",
    #                                       "dash_refill",
    #                                       "breakables"}, world.player))
    # set_rule(world.multiworld.get_location("strawberry_23", world.player),
    #          lambda state: state.has_all({"cassette",
    #                                       "dash_refill",
    #                                       "coin"}, world.player))
    # set_rule(world.multiworld.get_location("strawberry_24", world.player),
    #          lambda state: state.has_all({"cassette",
    #                                       "traffic_block",
    #                                       "dash_refill"}, world.player))
    # set_rule(world.multiworld.get_location("strawberry_25", world.player),
    #          lambda state: state.has_all({"cassette",
    #                                       "dash_refill",
    #                                       "double_dash_refill"}, world.player))
    # set_rule(world.multiworld.get_location("strawberry_26", world.player),
    #          lambda state: state.has_all({"cassette",
    #                                       "dash_refill"}, world.player))
    # set_rule(world.multiworld.get_location("strawberry_27", world.player),
    #          lambda state: state.has_all({"cassette",
    #                                       "feather",
    #                                       "coin",
    #                                       "dash_refill"}, world.player))
    # set_rule(world.multiworld.get_location("strawberry_28", world.player),
    #          lambda state: state.has_all({"cassette",
    #                                       "feather",
    #                                       "coin",
    #                                       "dash_refill"}, world.player))
    # set_rule(world.multiworld.get_location("strawberry_29", world.player),
    #          lambda state: state.has_all({"cassette",
    #                                       "feather",
    #                                       "coin",
    #                                       "dash_refill"}, world.player))
    # set_rule(world.multiworld.get_location("strawberry_30", world.player),
    #          lambda state: state.has_all({"cassette",
    #                                       "feather",
    #                                       "traffic_block",
    #                                       "spring",
    #                                       "breakables",
    #                                       "dash_refill",
    #                                       "double_dash_refill"}, world.player))

    # Completion condition.
    # victory_loc = MyGameLocation(self.player, "Defeat the Final Boss", None, final_boss_arena_region)
    # victory_loc.place_locked_item(MyGameItem("Victory", ItemClassification.progression, None, world.player))
    # world.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", world.player)
    # set_rule(victory_loc, lambda state: state.has("Boss Defeating Sword", world.player))

    # victory_item = Borderlands2Item("Victory", ItemClassification.progression, None, world.player)
    # # victory_item = world.create_event("Victory")
    # boss_location = Borderlands2Location(world.player, "Final Boss", None, world.get_region("Menu"))
    # boss_location.place_locked_item(victory_item)
    #
    # world.multiworld.completion_condition[world.player] = lambda state: (state.has("Victory", world.player))
    # world.get_region("Menu").locations.append(victory_item)
