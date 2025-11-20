from typing import List

from BaseClasses import ItemClassification, Region, Tutorial
from worlds.AutoWorld import WebWorld, World
from .Items import Borderlands2Item, item_data_table, bl2_base_id, item_name_to_id, item_descriptions
from .Locations import Borderlands2Location, location_data_table, location_name_to_id, location_descriptions
from .Options import Borderlands2Options
from worlds.LauncherComponents import components, Component, launch_subprocess, Type


class Borderlands2WebWorld(WebWorld):
    theme = "ice"

    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Borderlands 2 for Multiworld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["EdricY"]
    )]


def launch_client():
    from .Client import launch
    launch_subprocess(launch, name='Borderlands 2 Client')


components.append(Component("Borderlands 2 Client",
                            func=launch_client,
                            component_type=Type.CLIENT))


class Borderlands2World(World):
    """
     Borderlands 2 is a looter shooter we all love.
    """

    game = "Borderlands 2"
    web = Borderlands2WebWorld()
    options_dataclass = Borderlands2Options
    options: Borderlands2Options
    location_name_to_id = location_name_to_id
    location_descriptions = location_descriptions
    item_name_to_id = item_name_to_id
    item_descriptions = item_descriptions

    def create_item(self, name: str) -> Borderlands2Item:
        return Borderlands2Item(name, item_data_table[name].type, item_data_table[name].code, self.player)

    def create_items(self) -> None:
        item_pool: List[Borderlands2Item] = []
        item_pool += [self.create_item(name) for name in item_data_table.keys()]
        item_pool += [self.create_item("Weapon Slot")]  # 2 total weapon slots
        item_pool += [self.create_item("Money Cap") for _ in range(3)]  # money cap is 4 stages
        item_pool += [self.create_item("5 Skill Points") for _ in range(5)]  # hit 30 at least

        # fill leftovers
        location_count = len(location_name_to_id)
        leftover = location_count - len(item_pool)
        item_pool += [self.create_item(self.get_filler_item_name()) for _ in range(leftover)]

        self.multiworld.itempool += item_pool

    def create_regions(self) -> None:
        menu_region = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu_region)

        menu_region.add_locations({
            location_name: location_data.address for location_name, location_data in location_data_table.items()
        }, Borderlands2Location)

        # setup victory condition (as "event" with None address/code)
        victory_location = Borderlands2Location(self.player, "Victory Location", None, menu_region)
        victory_item = Borderlands2Item("Victory", ItemClassification.progression, None, self.player)
        victory_location.place_locked_item(victory_item)
        menu_region.locations.append(victory_location)
        self.multiworld.completion_condition[self.player] = lambda state: (state.has("Victory", self.player))

        # menu_region.locations.append(
        #     Borderlands2Location(self.player, "Final Boss", None, menu_region)
        # )

        # from .Regions import region_data_table
        # # Create regions.
        # for region_name in region_data_table.keys():
        #     region = Region(region_name, self.player, self.multiworld)
        #     self.multiworld.regions.append(region)
        #
        # # Create locations.
        # for region_name, region_data in region_data_table.items():
        #     region = self.multiworld.get_region(region_name, self.player)
        #     region.add_locations({
        #         location_name: location_data.address for location_name, location_data in location_data_table.items()
        #         if location_data.region == region_name
        #     }, Borderlands2Location)
        #
        #     if region_name == "Menu":
        #         region.locations.append(Borderlands2Location(self.player, "Final Boss", None, region))
        #
        #     region.add_exits(region_data_table[region_name].connecting_regions)

    def get_filler_item_name(self) -> str:
        return "5 Skill Points"

    def set_rules(self) -> None:
        from .Rules import set_rules
        set_rules(self)

    def fill_slot_data(self):
        return {
            "death_link": self.options.death_link.value,
            "death_link_mode": self.options.death_link_mode.value
        }
