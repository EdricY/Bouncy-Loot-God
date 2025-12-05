from typing import List

from BaseClasses import ItemClassification, Region, Tutorial
from worlds.AutoWorld import WebWorld, World
from worlds.LauncherComponents import components, Component, launch_subprocess, Type
from .Items import Borderlands2Item, item_data_table, bl2_base_id, item_name_to_id, item_descriptions, bl2_base_id
from .Locations import Borderlands2Location, location_data_table, location_name_to_id, location_descriptions, get_region_from_loc_name
from .Options import Borderlands2Options
from .Regions import region_data_table
from .archi_defs import loc_name_to_id, item_id_to_name


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
    goal = loc_name_to_id["Enemy BloodshotRamparts: W4R-D3N"]  # without base id
    skill_pts_total = 0
    filler_counter = 0

    def create_item(self, name: str) -> Borderlands2Item:
        return Borderlands2Item(name, item_data_table[name].type, item_data_table[name].code, self.player)

    def create_filler(self) -> Borderlands2Item:
        self.filler_counter += 1
        if self.filler_counter % 3 == 1:
            if self.skill_pts_total < 126:  # max at 126 skill points
                self.skill_pts_total += 3
                return self.create_item("3 Skill Points")

        if self.filler_counter % 3 == 2:
            return self.create_item("10 Eridium")

        return self.create_item("$100")

    def create_items(self) -> None:
        item_pool: List[Borderlands2Item] = []
        item_pool += [self.create_item(name) for name in item_data_table.keys()]  # 1 of everything to start
        item_pool += [self.create_item("Weapon Slot")]  # 2 total weapon slots
        item_pool += [self.create_item("Progressive Money Cap") for _ in range(3)]  # money cap is 4 stages
        item_pool += [self.create_item("3 Skill Points") for _ in range(8)]  # hit 27 at least
        self.skill_pts_total += 3 * 9

        # setup jump checks
        if self.options.jump_checks.value == 0:
            # remove jump check
            item_pool = [item for item in item_pool if not item.name == "Progressive Jump"]
        else:
            # add num checks - 1
            jumps_to_add = self.options.jump_checks.value - 1
            item_pool += [self.create_item("Progressive Jump") for _ in range(jumps_to_add)]

        # remove travel items (entrance locks)
        if self.options.entrance_locks.value == 0:
            item_pool = [item for item in item_pool if not item.name.startswith("Travel: ")]

        # fill leftovers
        location_count = len(location_name_to_id)
        leftover = location_count - len(item_pool)
        for _ in range(leftover - 1):
            item_pool += [self.create_filler()]

        self.multiworld.itempool += item_pool

    def create_regions(self) -> None:
        # menu_region = Region("Menu", self.player, self.multiworld)
        # self.multiworld.regions.append(menu_region)

        goal_name = "Enemy AridNexusBadlands: Saturn" if self.options.goal.value == 0 \
            else "Enemy BloodshotRamparts: W4R-D3N"
        self.goal = loc_name_to_id[goal_name]

        loc_dict = {
            location_name: location_data.address for location_name, location_data in location_data_table.items()
        }

        # remove goal from locations
        del loc_dict[goal_name]

        # remove symbols
        if self.options.vault_symbols.value == 0:
            for location_name, location_data in location_data_table.items():
                if location_name.startswith("Symbol"):
                    del loc_dict[location_name]

        # remove vending machines
        if self.options.vending_machines.value == 0:
            for location_name, location_data in location_data_table.items():
                if location_name.startswith("Vending"):
                    del loc_dict[location_name]

        # create regions
        for name, region_data in region_data_table.items():
            region = Region(name, self.player, self.multiworld)
            self.multiworld.regions.append(region)


        # connect regions
        for name, region_data in region_data_table.items():
            region = self.multiworld.get_region(name, self.player)
            for c_region_name in region_data.connecting_regions:
                c_region = self.multiworld.get_region(c_region_name, self.player)
                exit_name = f"{region.name} to {c_region.name}"
                # TODO: do you have to (or is it better to) add all the exits in one go?
                region.add_exits({c_region.name: exit_name})

        # add locations to regions
        for name, addr in loc_dict.items():
            loc_data = location_data_table[name]
            region_name = loc_data.region
            region = self.multiworld.get_region(region_name, self.player)
            region.add_locations({name: addr}, Borderlands2Location)


        # setup victory condition (as "event" with None address/code)
        v_region_name = get_region_from_loc_name(goal_name)
        victory_region = self.multiworld.get_region(v_region_name, self.player)
        victory_location = Borderlands2Location(self.player, "Victory Location", None, victory_region)
        victory_item = Borderlands2Item("Victory: " + goal_name, ItemClassification.progression, None, self.player)
        victory_location.place_locked_item(victory_item)
        victory_region.locations.append(victory_location)

        self.multiworld.completion_condition[self.player] = lambda state: (
            state.has("Victory: " + goal_name, self.player)
        )

        from Utils import visualize_regions
        visualize_regions(self.multiworld.get_region("Menu", self.player), "my_world.puml")
        print("visualize_regions")

    def get_filler_item_name(self) -> str:
        return "$100"

    def set_rules(self) -> None:
        from .Rules import set_rules
        set_rules(self)

    def fill_slot_data(self):
        return {
            "goal": self.goal,
            "delete_starting_gear": self.options.delete_starting_gear.value,
            "receive_gear": self.options.receive_gear.value,
            "vault_symbols": self.options.vault_symbols.value,
            "vending_machines": self.options.vending_machines.value,
            "entrance_locks": self.options.entrance_locks.value,
            "jump_checks": self.options.jump_checks.value,
            "max_jump_height": self.options.max_jump_height.value,
            "death_link": self.options.death_link.value,
            "death_link_mode": self.options.death_link_mode.value
        }
