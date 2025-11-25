from typing import List

from BaseClasses import ItemClassification, Region, Tutorial
from worlds.AutoWorld import WebWorld, World
from worlds.LauncherComponents import components, Component, launch_subprocess, Type
from .Items import Borderlands2Item, item_data_table, bl2_base_id, item_name_to_id, item_descriptions, bl2_base_id
from .Locations import Borderlands2Location, location_data_table, location_name_to_id, location_descriptions
from .Options import Borderlands2Options
from .archi_defs import loc_name_to_id


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
    goal = loc_name_to_id["Warrior"]  # without base id

    def create_item(self, name: str) -> Borderlands2Item:
        return Borderlands2Item(name, item_data_table[name].type, item_data_table[name].code, self.player)

    def create_items(self) -> None:
        item_pool: List[Borderlands2Item] = []
        item_pool += [self.create_item(name) for name in item_data_table.keys()]  # 1 of everything to start
        item_pool += [self.create_item("Weapon Slot")]  # 2 total weapon slots
        item_pool += [self.create_item("Money Cap") for _ in range(3)]  # money cap is 4 stages
        item_pool += [self.create_item("3 Skill Points") for _ in range(8)]  # hit 27 at least

        # fill leftovers
        location_count = len(location_name_to_id)
        leftover = location_count - len(item_pool)
        item_pool += [self.create_item(self.get_filler_item_name()) for _ in range(leftover)]

        self.multiworld.itempool += item_pool

    def create_regions(self) -> None:
        menu_region = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions.append(menu_region)

        goal_name = "Warrior" if self.options.goal.value == 0 else "W4R-D3N"
        self.goal = loc_name_to_id[goal_name]
        del location_data_table[goal_name]
        del location_name_to_id[goal_name]
        del location_descriptions[goal_name]

        menu_region.add_locations({
            location_name: location_data.address for location_name, location_data in location_data_table.items()
        }, Borderlands2Location)

        # setup victory condition (as "event" with None address/code)
        victory_location = Borderlands2Location(self.player, "Victory Location", None, menu_region)
        victory_item = Borderlands2Item("Victory", ItemClassification.progression, None, self.player)
        victory_location.place_locked_item(victory_item)
        menu_region.locations.append(victory_location)
        self.multiworld.completion_condition[self.player] = lambda state: (state.has("Victory", self.player))

    def get_filler_item_name(self) -> str:
        return "3 Skill Points"

    def set_rules(self) -> None:
        from .Rules import set_rules
        set_rules(self)

    def fill_slot_data(self):
        return {
            "goal": self.goal,
            "receive_guns": self.options.death_link.value,
            "death_link": self.options.death_link.value,
            "death_link_mode": self.options.death_link_mode.value
        }
