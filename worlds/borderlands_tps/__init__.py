from typing import List, Any

from BaseClasses import Item, ItemClassification, Region, Tutorial, LocationProgressType, MultiWorld
from worlds.AutoWorld import WebWorld, World
from worlds.LauncherComponents import components, Component, launch_subprocess, Type
from .Rules import set_world_rules
from .Locations import BorderlandsTPSLocation, location_data_table, location_name_to_id, location_descriptions, bltps_base_id
from .Items import BorderlandsTPSItem
from .Options import BorderlandsTPSOptions
from .Regions import region_data_table, progressive_travel_dict, progressive_travel_items
from .archi_defs import loc_name_to_id, item_id_to_name, gear_data_table, item_data_table, item_name_to_id as item_name_to_raw_id
import random
from copy import deepcopy

VERSION = "0.6.0"

chest_check_option_to_prefix = {
    "Dahl Chests" : "Chest ", #trailing space is intentional
    "Red Chests" : "Red Chest ",
    "Moonstone Chests" : "MoonChest ",
}


class BorderlandsTPSWebWorld(WebWorld):
    theme = "ice"

    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Borderlands The Pre-Sequel for Multiworld.",
        "English",
        "setup_en.md",
        "setup/en",
        ["EdricY"]
    )]


def launch_client():
    from .Client import launch
    launch_subprocess(launch, name='Borderlands The Pre-Sequel Client')


components.append(Component("Borderlands The Pre-Sequel Client",
                            func=launch_client,
                            component_type=Type.CLIENT))

bl_tps_name = "Borderlands The Pre-Sequel"
class BorderlandsTPSWorld(World):
    """
     Borderlands The Pre-Sequel is a looter shooter we all love.
    """
    

    game = bl_tps_name
    web = BorderlandsTPSWebWorld()
    
    # UT Yaml-less flag
    ut_can_gen_without_yaml = True
    
    options_dataclass = BorderlandsTPSOptions
    options: BorderlandsTPSOptions
    location_name_to_id = location_name_to_id
    location_descriptions = location_descriptions
    item_name_to_id = {name: bltps_base_id + id for name, id in item_name_to_raw_id.items()}
    item_name_groups = {
        "BasicCombat": { "License: Common Pistol", "License: Uncommon Pistol", "Melee" },
        "BasicMobility": { "Progressive Jump", "Progressive Sprint", "License: Common Oz Kit", "License: Uncommon Oz Kit",  },
        "GrenadeMod": { "License: Common GrenadeMod", "License: Uncommon GrenadeMod", "License: Rare GrenadeMod", "License: VeryRare GrenadeMod", "License: Legendary GrenadeMod", "License: Unique GrenadeMod" },
        "Shield": { "License: Common Shield", "License: Uncommon Shield", "License: Rare Shield", "License: VeryRare Shield", "License: Legendary Shield", "License: Unique Shield" },
        "Pistol": { "License: Common Pistol", "License: Uncommon Pistol", "License: Rare Pistol", "License: VeryRare Pistol", "License: Legendary Pistol", "License: Glitch Pistol", "License: Unique Pistol" },
        "Shotgun": { "License: Common Shotgun", "License: Uncommon Shotgun", "License: Rare Shotgun", "License: VeryRare Shotgun", "License: Legendary Shotgun", "License: Glitch Shotgun", "License: Unique Shotgun" },
        "SMG": { "License: Common SMG", "License: Uncommon SMG", "License: Rare SMG", "License: VeryRare SMG", "License: Legendary SMG", "License: Glitch SMG", "License: Unique SMG" },
        "SniperRifle": { "License: Common SniperRifle", "License: Uncommon SniperRifle", "License: Rare SniperRifle", "License: VeryRare SniperRifle", "License: Legendary SniperRifle", "License: Glitch SniperRifle", "License: Unique SniperRifle" },
        "AssaultRifle": { "License: Common AssaultRifle", "License: Uncommon AssaultRifle", "License: Rare AssaultRifle", "License: VeryRare AssaultRifle", "License: Legendary AssaultRifle", "License: Glitch AssaultRifle", "License: Unique AssaultRifle" },
        "RocketLauncher": { "License: Common RocketLauncher", "License: Uncommon RocketLauncher", "License: Rare RocketLauncher", "License: VeryRare RocketLauncher", "License: Legendary RocketLauncher", "License: Glitch RocketLauncher", "License: Unique RocketLauncher" },
        "Laser": { "License: Common Laser", "License: Uncommon Laser", "License: Rare Laser", "License: VeryRare Laser", "License: Legendary Laser", "License: Glitch Laser", "License: Unique Laser" },
        "Oz Kit": { "License: Common Oz Kit", "License: Uncommon Oz Kit" },
    }

    # explicit_indirect_conditions = False # testing with this, hopefully can remove it later

    def __init__(self, multiworld: MultiWorld, player: int):
        super(BorderlandsTPSWorld, self).__init__(multiworld, player)
        self.filler_gear_names = []
        self.restricted_regions = set()
        self.goals = set()  # without base id
        self.skill_pts_total = 0
        self.filler_counter = 0
        
        self.filler_sdu_dict = {
            "Max Ammo Pistol": 7,
            "Max Ammo Shotgun": 7,
            "Max Ammo SMG": 7,
            "Max Ammo SniperRifle": 7,
            "Max Ammo AssaultRifle": 7,
            "Max Ammo RocketLauncher": 7,
            "Max Ammo Laser": 7,
            "Max Grenade Count": 7,
            "Backpack Upgrade": 9,
            # "Bank Storage Upgrade": 9,
        }
        self.filler_moxxtail = [
            "Moxxtail: Moxxis' Choice", 
            "Moxxtail: Brick's Fist", 
            "Moxxtail: Fanalian Toddy", 
            "Moxxtail: Gargle Blaster", 
            "Moxxtail: Hot Gazpacho", 
            "Moxxtail: Lemon Lime & Bullets", 
            "Moxxtail: Penargilon Kangaroo", 
            "Moxxtail: Replicated Kali-fal", 
            "Moxxtail: Squill Syrup"
        ]

    def try_get_entrance(self, entrance_name):
        try:
            return self.multiworld.get_entrance(entrance_name, self.player)
        except KeyError:
            # print("couldn't find entrance: " + entrance_name)
            return None

    def try_get_location(self, loc_name):
        try:
            return self.multiworld.get_location(loc_name, self.player)
        except KeyError:
            # print("couldn't find location: " + loc_name)
            return None

    def try_get_region(self, reg_name):
        try:
            return self.multiworld.get_region(reg_name, self.player)
        except KeyError:
            # print("couldn't find location: " + reg_name)
            return None


    def generate_early(self):
        if self.options.remove_claptrap_checks.value == 1:
            self.restricted_regions.update([region for region in region_data_table if region_data_table[region].dlc_group == "claptrap"])

        if self.options.remove_shock_drop_checks.value == 1:
            self.restricted_regions.update([region for region in region_data_table if region_data_table[region].dlc_group == "shock_drop"])

        if self.options.remove_holodome_checks.value == 1:
            self.restricted_regions.update([region for region in region_data_table if region_data_table[region].dlc_group == "holodome"])

        if self.options.remove_base_game_checks.value == 1:
            self.restricted_regions.update([region for region in region_data_table if region_data_table[region].dlc_group == "basegame"])
            self.restricted_regions.update([region for region in region_data_table if region_data_table[region].dlc_group == "basegame_side"])

        if self.options.remove_specific_region_checks:
            self.restricted_regions.update(self.options.remove_specific_region_checks.value)

        all_filler_gear = [key for key in item_data_table.keys() if key.startswith("Filler Gear: ")]
        unique_filler = [key for key in all_filler_gear if key.replace("Filler Gear: ", "") not in gear_data_table]
        non_unique_filler = [key for key in all_filler_gear if key.replace("Filler Gear: ", "") in gear_data_table]

        if self.options.filler_gear.value == 1:  # unique
            self.filler_gear_names = unique_filler
        elif self.options.filler_gear.value == 2:  # rarity_groups
            self.filler_gear_names = non_unique_filler
        elif self.options.filler_gear.value == 3:  # both
            self.filler_gear_names = all_filler_gear
        else:  # none
            self.filler_gear_names = []

        self.filler_gear_names = [f for f in self.filler_gear_names if item_data_table[f].region not in self.restricted_regions]

        if set(self.options.filler_item_rotation.value).issubset(set(["sdu", "gear", "3 Skill Points"])):
            print("BL TPS Filler Pool is made of only exhastible elements. Consider changing filler_item_rotation.")

        # if self.options.remove_raidboss_checks.value == 1:
        #     self.restricted_regions.update(["WingedStorm", "WrithingDeep","TerramorphousPeak"])

        # goal setup
        for goal_name in self.options.goal.value:
            if goal_name not in loc_name_to_id:
                raise Exception(f"Goal [{goal_name}] not found in location table")
            self.goals.add(loc_name_to_id[goal_name]) # without base id
        if len(self.goals) == 0:
            raise Exception("No goals selected.")
        # self.options.exclude_locations.value.add(goal_name)

        # TODO: maybe add regions beyond the goal to restricted regions, or we can just expect the yaml to add them to remove_specific_region_checks
        # Implement Universal Tracker support - reset all options to those from interpret_slot_data if applicable.
        if hasattr(self.multiworld, "re_gen_passthrough"):
            if bl_tps_name in self.multiworld.re_gen_passthrough:
                for key, val in self.multiworld.re_gen_passthrough[bl_tps_name].items():
                    try:
                        getattr(self.options, key).value = val
                    except AttributeError:
                        pass

    def is_gear_license_excluded(self, name: str) -> bool:
        if self.options.gear_licenses.value <= 1 and name.startswith("License: Glitch"):
            return True
        if self.options.gear_licenses.value == 0 and name.startswith("License: "):
            return True
        return False

    def create_event(self, name: str) -> BorderlandsTPSItem:
        return BorderlandsTPSItem(name, ItemClassification.progression, None, self.player)
    
    def create_event_at(self, name: str, region_name: str) -> BorderlandsTPSItem:
        reg = self.try_get_region(region_name)
        loc = BorderlandsTPSLocation(self.player, name, None, reg)
        item = self.create_event(name)
        loc.place_locked_item(item)
        reg.locations.append(loc)
        return (item, loc)

    def create_item(self, name: str) -> BorderlandsTPSItem:
        item_data = item_data_table[name]
        kind_str = item_data.item_kind
        kind = ItemClassification[kind_str]
        if "gear" in item_data.tags:
            kind = ItemClassification.progression
        return BorderlandsTPSItem(name, kind, self.item_name_to_id[name], self.player) # note: self.item_name_to_id includes bltps_base_id

    def create_filler(self) -> BorderlandsTPSItem:
        if not self.options.filler_item_rotation.value:
            return self.create_item("10 Moonstones")
        self.filler_counter += 1

        num_branches = len(self.options.filler_item_rotation.value)
        branch = self.filler_counter % num_branches
        attempts = 0
        while attempts < 10:
            attempts += 1
            item_name = self.options.filler_item_rotation.value[branch]

            if item_name == "sdu":
                max_value = max(self.filler_sdu_dict.values())
                if max_value > 0:
                    max_items = [item for item, value in self.filler_sdu_dict.items() if value == max_value]
                    filler_sdu = random.choice(max_items)
                    self.filler_sdu_dict[filler_sdu] -= 1
                    return self.create_item(filler_sdu)

            elif item_name == "gear":
                if self.filler_gear_names:
                    gear_name = random.choice(self.filler_gear_names)
                    self.filler_gear_names.remove(gear_name)
                    return self.create_item(gear_name)
                
            elif item_name == "Moxxtails":
                if self.filler_moxxtail:
                    return self.create_item(random.choice(self.filler_moxxtail))

            elif item_name == "3 Skill Points":
                if self.skill_pts_total < 120:
                    self.skill_pts_total += 3
                    return self.create_item("3 Skill Points")

            else:
                return self.create_item(item_name)

            # nothing returned yet, pick a new branch for next attempt
            skip_amt = self.filler_counter // num_branches # skip forward by amount of times this entry has been selected
            skip_amt = (skip_amt % (num_branches - 1)) + 1 # mod by len-1 to avoid jumping to self
            branch = (branch + skip_amt) % (num_branches)

        print("BL TPS Filler Pool Exhausted... consider changing filler_item_rotation")
        return self.create_item("10 Moonstones") # fallback if all attempts failed

    def create_items(self) -> None:
        item_pool: List[BorderlandsTPSItem] = []
        item_pool += [self.create_item(name) for name in item_data_table.keys() if not (name == "Melee" and self.options.start_with_melee.value)]  # 1 of everything to start
        item_pool += [self.create_item("Progressive Weapon Slot")]  # 2 total weapon slots
        item_pool += [self.create_item("Progressive Money Cap") for _ in range(7)]  # money cap is 8 stages
        item_pool += [self.create_item("3 Skill Points") for _ in range(7)]  # hit 27 at least
        self.skill_pts_total += 3 * 9 # 1 progressive + 8 filler
        self.filler_sdu_dict = { k : v-1 for k, v in self.filler_sdu_dict.items() } # decrement filler sdus by 1
        if self.options.start_with_melee: 
            self.push_precollected(self.create_item("Melee"))
        # setup jump checks
        if self.options.jump_checks.value == 0:
            # remove jump check
            item_pool = [item for item in item_pool if not item.name == "Progressive Jump"]
        else:
            # add num checks - 1
            jumps_to_add = self.options.jump_checks.value - 1
            item_pool += [self.create_item("Progressive Jump") for _ in range(jumps_to_add)]

        # setup sprint checks
        if self.options.sprint_checks.value == 0:
            # remove sprint check
            item_pool = [item for item in item_pool if not item.name == "Progressive Sprint"]
        else:
            # add num checks - 1
            sprints_to_add = self.options.sprint_checks.value - 1
            item_pool += [self.create_item("Progressive Sprint") for _ in range(sprints_to_add)]

        # setup trap spawns
        if self.options.spawn_traps.value == 0:
            # remove trap spawns
            item_pool = [item for item in item_pool if not item.name.startswith("Trap Spawn: ")]
        else:
            # add num traps - 1
            traps_to_add = self.options.spawn_traps.value - 1
            trap_items = [item for item in item_pool if item.name.startswith("Trap Spawn: ")]
            trap_items = trap_items * traps_to_add
            item_pool += trap_items
        # setup trap
        if self.options.effect_traps.value == 0:
            # remove trap
            item_pool = [item for item in item_pool if not item.name.startswith("Trap: ")]
        else:
            # add num traps - 1
            traps_to_add = self.options.effect_traps.value - 1
            trap_items = [item for item in item_pool if item.name.startswith("Trap: ")]
            trap_items = trap_items * traps_to_add
            item_pool += trap_items

        # remove existing progressive travel items, handled later
        item_pool = [item for item in item_pool if not item.name.startswith("Progressive Travel: ")]

        restricted_travel_items = [region_data_table[r].travel_item_name for r in self.restricted_regions]

        new_pool = []

        # reconstruct pool based on remaining options
        for item in item_pool:
            item_data = item_data_table[item.name]

            # skip filler gear for now
            if item.name.startswith("Filler Gear"):
                continue
            # skip override items (should only be used in yaml)
            if item.name.startswith("Override"):
                continue

            # skip travel items
            if item.name.startswith("Travel: "):
                if self.options.entrance_locks.value == 0:
                    continue
                if item.name in restricted_travel_items: # skip restricted region Travel Items
                    continue

            if item.name.startswith("Reward"):
                # skip quest rewards
                if self.options.quest_reward_items.value == 0:
                    continue
                # skip non-gear quest rewards
                if self.options.quest_reward_items.value == 2 or self.options.quest_reward_items.value == 4:
                    if item_data_table[item.name].is_non_gear_reward:
                        continue
                # skip quest rewards from restricted regions
                if self.options.quest_reward_items.value == 3 or self.options.quest_reward_items.value == 4:
                    if item_data_table[item.name].region in self.restricted_regions:
                        continue

            # skip gear licenses
            if item.name.startswith("License:") and self.is_gear_license_excluded(item.name):
                continue

            # item should be included
            new_pool.append(item)

        item_pool = new_pool

        # replace travel items with progressive travel items
        if len(self.options.progressive_travel_groups.value) > 0:
            for group in self.options.progressive_travel_groups.value:
                for r in progressive_travel_dict[group]:
                    reg = region_data_table.get(r)
                    if not reg:
                        continue
                    i = next((idx for idx, item in enumerate(item_pool) if item.name == reg.travel_item_name), None)
                    if i is not None:
                        item_pool[i] = self.create_item(progressive_travel_items[group])

        # fill leftovers
        location_count = len(self.multiworld.get_unfilled_locations(self.player))
        leftover = location_count - len(item_pool)
        # print("Adding Filler Checks: " + str(leftover))
        for _ in range(leftover):
            item_pool += [self.create_filler()]

        self.multiworld.itempool += item_pool

    def create_regions(self) -> None:
        loc_dict = {
            location_name: location_id for location_name, location_id in self.location_name_to_id.items()
        }
        event_locations = []
        # first pass: easy removal rules
        for location_name, location_data in location_data_table.items():
            # remove symbols
            if self.options.vault_symbols.value == 0:
                if location_name.startswith("Symbol"):
                    loc_dict[location_name] = None
                if location_name.endswith("Cult of the Vault"):
                    loc_dict[location_name] = None

            # remove vending machines
            if self.options.vending_machines.value == 0:
                if location_name.startswith("Vending"):
                    loc_dict[location_name] = None

            # remove quests
            if self.options.quest_completion_checks.value != 1:
                if location_name.startswith("Quest"):
                    if self.options.quest_completion_checks.value == 0:
                        loc_dict[location_name] = None
                        event_locations.append(location_name)
                    elif self.options.quest_completion_checks.value == 2 and "story" not in location_data.tags:
                        loc_dict[location_name] = None
                        event_locations.append(location_name)
                    elif self.options.quest_completion_checks.value == 3 and "story" in location_data.tags:
                        loc_dict[location_name] = None
                        event_locations.append(location_name)

            # remove generic mob checks
            if self.options.generic_mob_checks.value == 0:
                if location_name.startswith("Generic"):
                    loc_dict[location_name] = None

            # remove challenge checks
            if self.options.challenge_checks.value != 1:
                if location_name.startswith("Challenge") or location_name.startswith("Special"):
                    if self.options.challenge_checks.value == 0:
                        loc_dict[location_name] = None
                    elif self.options.challenge_checks.value == 2 and "reg-based" not in location_data.tags:
                        loc_dict[location_name] = None
                    elif self.options.challenge_checks.value == 3 and "general" not in location_data.tags:
                        loc_dict[location_name] = None

            # remove chest checks
            for opt in self.options.chest_type_checks.valid_keys:
                if opt not in self.options.chest_type_checks.value:
                    if location_name.startswith(chest_check_option_to_prefix[opt]):
                        loc_dict[location_name] = None

            # remove co-op checks
            if self.options.remove_coop_checks.value != 0:
                v = location_data.coop_type
                if v and v <= self.options.remove_coop_checks.value:
                    loc_dict[location_name] = None

            # remove missable checks
            if self.options.remove_missable_checks.value != 0:
                if "missable" in location_data.tags:
                    loc_dict[location_name] = None

            # remove raidboss checks
            if self.options.remove_raidboss_checks.value == 1:
                if "raidboss" in location_data.tags:
                    loc_dict[location_name] = None

            # remove checks above max level
            if self.options.max_level_checks.value != 0:
                all_levels = [v.level for v in [location_data] + location_data.alternates]
                if all_levels and all(l > self.options.max_level_checks.value for l in all_levels):
                    loc_dict[location_name] = None

            # remove level checks below override level
            if "Override Level 15" in self.options.start_inventory.value:
                if location_name.startswith("Level ") and location_data.level <= 15:
                    loc_dict[location_name] = None
            if "Override Level 30" in self.options.start_inventory.value:
                if location_name.startswith("Level ") and location_data.level <= 30:
                    loc_dict[location_name] = None

            # remove specified locations
            if self.options.remove_locations.value:
                if location_name in self.options.remove_locations.value:
                    loc_dict[location_name] = None

        # remove rarity checks
        if self.options.gear_rarity_checks.value != 4:
            for gear_name, location_data in gear_data_table.items():
                location_name = gear_name + " Found"
                if self.options.gear_rarity_checks.value <= 1 and gear_name.startswith("Glitch"):
                    loc_dict[location_name] = None
                elif self.options.gear_rarity_checks.value == 0 and "gear" in location_data.tags:
                    loc_dict[location_name] = None

        # remove if all alternatives contain a restricted region
        for location_name, location_data in location_data_table.items():
            if loc_dict[location_name] is None:
                # already removed, skip
                continue
            all_alternatives = [location_data] + location_data.alternates
            for alt in all_alternatives:
                regions_required = [alt.region] + alt.other_req_regions
                if not any(r in self.restricted_regions for r in regions_required):
                    # this alternative is valid
                    break
            else:
                # all alternatives contain a restricted region
                loc_dict[location_name] = None

        # re-add included_locations
        if self.options.include_locations.value:
            for location_name in self.options.include_locations.value:
                if location_name in location_name_to_id:
                    loc_dict[location_name] = location_name_to_id[location_name]

        # re-add goal location in case it got removed by another setting
        for goal_name in self.options.goal.value:
            loc_dict[goal_name] = location_name_to_id[goal_name]

        # create regions
        for name, region_data in region_data_table.items():
            region = Region(name, self.player, self.multiworld)
            self.multiworld.regions.append(region)
            # # attempting to use events for region detection
            # event_loc = self.try_get_location(f"Region Reached - {name}")
            # if not event_loc:
            #     event_loc = BorderlandsTPSLocation(self.player, f"Region Reached - {name}", None, region)
            #     event_loc.place_locked_item(BorderlandsTPSItem(f"Region Reached - {name}", ItemClassification.progression, None, self.player))
            #     region.locations.append(event_loc)

        # connect regions
        for name, region_data in region_data_table.items():
            region = self.multiworld.get_region(name, self.player)
            for c_region_name in region_data.connecting_regions:
                c_region = self.multiworld.get_region(c_region_name, self.player)
                exit_name = f"{region.name} to {c_region.name}"
                region.add_exits({c_region.name: exit_name})

        menu_reg = self.multiworld.get_region("Menu", self.player)
        # add all locations to Menu, region requirements handled in Rules.py
        for name, addr in loc_dict.items():
            if addr is None:
                continue
            loc_data = location_data_table[name]
            menu_reg.add_locations({name: addr}, BorderlandsTPSLocation)
        for location in event_locations:
            data = location_data_table[location]
            if not data:
                print(f"Unable to find location_data for: {location}")
                continue
            if location.startswith("Quest: "):
                if self.options.quest_completion_checks.value == 0:
                    (item, loc) = self.create_event_at(location, data.region)
                elif self.options.quest_completion_checks.value == 2 and "story" not in data.tags:
                    (item, loc) = self.create_event_at(location, data.region)
                elif self.options.quest_completion_checks.value == 3 and "story" in data.tags:
                    (item, loc) = self.create_event_at(location, data.region)
                if loc:
                    loc.show_in_spoiler = False
        # setup goal location. place local filler item there. TODO: maybe replace with "Nothing"
        for goal_name in self.options.goal.value:
            self.multiworld.get_location(goal_name, self.player).place_locked_item(self.create_item("$100"))

        self.multiworld.completion_condition[self.player] = lambda state: all(
            state.can_reach_location(goal_name, self.player) for goal_name in self.options.goal.value
        )

        # generate region graph (for debugging/visualization)
        # from Utils import visualize_regions
        # print("visualize_regions")
        # visualize_regions(self.multiworld.get_region("Menu", self.player), "my_world.puml")

    def get_filler_item_name(self) -> str:
        return "$100"

    def set_rules(self) -> None:
        set_world_rules(self)

    # def pre_fill(self) -> None:
    #     pass

    def fill_slot_data(self):
        slot_data = {
            "version": VERSION,
            "goals": self.goals,
            "delete_starting_gear": self.options.delete_starting_gear.value,
            "gear_licenses": self.options.gear_licenses.value,
            "filler_gear": self.options.filler_gear.value,
            "receive_gear": self.options.receive_gear.value,
            "vault_symbols": self.options.vault_symbols.value,
            "vending_machines": self.options.vending_machines.value,
            "entrance_locks": self.options.entrance_locks.value,
            "progressive_travel_groups": self.options.progressive_travel_groups.value,
            "jump_checks": self.options.jump_checks.value,
            "max_jump_height": self.options.max_jump_height.value,
            "sprint_checks": self.options.sprint_checks.value,
            "max_sprint_speed": self.options.max_sprint_speed.value,
            "spawn_traps": self.options.spawn_traps.value,
            "quest_completion_checks": self.options.quest_completion_checks.value,
            "quest_reward_items": self.options.quest_reward_items.value,
            "generic_mob_checks": self.options.generic_mob_checks.value,
            #"named_enemy_checks": self.options.named_enemy_checks.value, Placeholder for when option gets added
            "gear_rarity_checks": self.options.gear_rarity_checks.value,
            "challenge_checks": self.options.challenge_checks.value,
            "chest_checks": min(1, len(self.options.chest_type_checks.value)), #enable chest checks if there is any
            "chest_type_checks": [chest_check_option_to_prefix[chest_check] for chest_check in self.options.chest_type_checks.value],
            "remove_missable_checks": self.options.remove_missable_checks.value,
            "remove_coop_checks": self.options.remove_coop_checks.value,
            "remove_claptrap_checks": self.options.remove_claptrap_checks.value,
            "remove_shock_drop_checks": self.options.remove_shock_drop_checks.value,
            "remove_holodome_checks": self.options.remove_holodome_checks.value,
            "remove_base_game_checks": self.options.remove_base_game_checks.value,
            "remove_specific_region_checks": self.options.remove_specific_region_checks.value,
            "restricted_regions": self.restricted_regions,
            "remove_locations": [location_name_to_id[loc] for loc in self.options.remove_locations.value],
            "include_locations": [location_name_to_id[loc] for loc in self.options.include_locations.value],
            "remove_raidboss_checks": self.options.remove_raidboss_checks.value,
            "max_level_checks": self.options.max_level_checks.value,
            "always_on_level": self.options.always_on_level.value,
            "death_link": self.options.death_link.value,
            "death_link_punishment": self.options.death_link_punishment.value,
            "death_link_send_mode": self.options.death_link_send_mode.value,
        }
        return slot_data

    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        # Implement Universal Tracker support - interpret the computed fields back to their generator values
        loc_id_to_name = {v: k for k, v in location_name_to_id.items()}
        chest_check_prefix_to_option = {v: k for k, v in chest_check_option_to_prefix.items()}
        inversed_slot_data = deepcopy(slot_data)
        #all fields that cant be directly applied to generator options needs to be handled here
        inversed_slot_data["chest_type_checks"] = [chest_check_prefix_to_option[prefix] for prefix in slot_data["chest_type_checks"]]
        inversed_slot_data["remove_locations"] = [loc_id_to_name[loc] for loc in slot_data["remove_locations"]]
        inversed_slot_data["include_locations"] = [loc_id_to_name[loc] for loc in slot_data["include_locations"]]
        return inversed_slot_data