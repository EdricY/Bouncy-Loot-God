from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Borderlands2World
from math import sqrt

from rule_builder.rules import Has, HasAll, Rule, CanReachRegion, HasAny, HasGroup, True_, False_, CanReachLocation

from .AtLeast import AtLeast

from .Regions import region_data_table, progressive_travel_items, progressive_travel_dict
from .Locations import Borderlands2Location, location_data_table
from .Items import Borderlands2Item
from .archi_defs import gear_data_table, quest_data_table, BL2ArchiData


def calc_jump_height(max_height_setting, num_slices, checks_amt): # needs to reflect the calculation done in sdkmod
    height_bonus = max_height_setting * 300
    max_height = 630 + height_bonus
    if num_slices == 0:
        return max_height
    frac = checks_amt / num_slices
    frac = sqrt(frac)
    return max(220, min(max_height, max_height * frac))

# TODO: try adding @cache to this
def amt_jump_checks_needed(world, jump_z_req):
    if world.options.jump_checks.value == 0:
        return 0
    if jump_z_req < 220:
        return 0
    if jump_z_req > 630:
        print(f"jump_z_req seems high: {jump_z_req}")
        return world.options.jump_checks.value
    checks_amt = 0
    height = 220
    while height < jump_z_req:
        checks_amt += 1
        height = calc_jump_height(world.options.max_jump_height.value, world.options.jump_checks.value, checks_amt)
    return checks_amt

def add_travel_item_rule(world, entrance, region):
    if not region:
        return
    t_item_name = region.travel_item_name
    if not t_item_name:
        return

    if region.name in world.options.remove_specific_region_checks.value:
        return

    if region.dlc_group in world.options.progressive_travel_groups.value:
        p_t_item_name = progressive_travel_items[region.dlc_group]
        # filter out locations in regions that have been excluded
        filtered_list = [name for name in progressive_travel_dict[region.dlc_group] if name not in world.options.remove_specific_region_checks.value]
        amt = filtered_list.index(region.name)
        world.try_add_rule(entrance, Has(p_t_item_name, amt))
    else:
        # print(entrance)
        # print(t_item_name)
        world.try_add_rule(entrance, Has(t_item_name))

def setup_level_rules(world: Borderlands2World):
    if world.options.always_on_level.value in (1, 2):
        # hold this list for later
        can_reach_rules = [CanReachRegion(r) for r in region_data_table.keys()]

    for lvl in range(1, 32): # 1 to 31
        rule = False_()

        # require one region within farming range
        for region_name, region_data in region_data_table.items():
            if region_data.min_level < lvl and region_data.max_level >= lvl:
                rule = rule | CanReachRegion(region_name)

        if world.options.always_on_level.value in (1, 2):
            # allow for basegame removal with always_on_level, require access to some arbitrary number of regions
            if lvl <= 5:
                rule = rule | AtLeast(3, *can_reach_rules)
            elif lvl <= 10:
                rule = rule | AtLeast(4, *can_reach_rules)
            elif lvl <= 15:
                rule = rule | AtLeast(6, *can_reach_rules)
            elif lvl <= 20:
                rule = rule | AtLeast(8, *can_reach_rules)
            elif lvl <= 25:
                rule = rule | AtLeast(10, *can_reach_rules)
            elif lvl <= 30:
                rule = rule | AtLeast(12, *can_reach_rules)

        # require previous level
        if lvl > 1:
            prev_lvl = lvl-1
            rule = rule & CanReachLocation(f"Lvl {prev_lvl}") 
            # we use CanReachLocation instead of Has to hide in playthrough (show_in_spoiler doesn't work as expected)
            # and using events instead of plain rules significantly improves generation time
        world.try_add_rule(f"Lvl {lvl}", rule)
        (lvl_item, lvl_loc) = world.create_event_at(f"Lvl {lvl}", "Menu")
        lvl_loc.show_in_spoiler = False

    if world.options.gear_licenses.value > 0:
        # require basic combat to surpass level 0
        world.try_add_rule("Lvl 1", HasAny("Melee", "License: Common Pistol"))
        # require reasonable loadout to surpass level 9
        world.try_add_rule("Lvl 10", HasAll("Melee", "License: Common Pistol", "License: Common Shield", "License: Common Shotgun", "License: Uncommon Pistol"))

    # alternative override for levels
    for lvl in range(1, 16):
        world.try_add_rule(f"Lvl {lvl}", Has("Override Level 15"), combine="or")
    for lvl in range(1, 31):
        world.try_add_rule(f"Lvl {lvl}", Has("Override Level 30"), combine="or")
    for lvl in range(1, 32):
        world.try_add_rule(f"Lvl {lvl}", Has("Override Level 80"), combine="or")

def setup_custom_rules(world: Borderlands2World):

    if "Forge" not in world.restricted_regions:
        # detecting end of Torgue DLC is a little weird.
        world.try_add_rule(
            "Torgue DLC Complete",
            CanReachRegion("Forge")
                & Has("Progressive Jump", amt_jump_checks_needed(world, 546)) 
                & Has("Crouch")
        )
        # TODO: maybe switch to requiring "Long Way To The Top" quest

        world.try_add_rule("Torgue Tokens Accessible", create_rule(world, BL2ArchiData("BadassCraterBar", 15), ""))

    world.try_add_rule("Seraph Crystals Accessible", 
        CanReachRegion("Sanctuary") # from black market
        | create_rule(world, BL2ArchiData("WashburneRefinery", 30, tags=["raidboss"], other_req_regions=["LeviathansLair"]), "") # hyperius
        | create_rule(world, BL2ArchiData("HaytersFolly", 30, tags=["raidboss"], other_req_regions=["LeviathansLair"]), "") # gee
        | create_rule(world, BL2ArchiData("PyroPetesBar", 30, req_rules=["Torgue DLC Complete"], tags=["raidboss"]), "") # pete
        | create_rule(world, BL2ArchiData("CandlerakksCrag", 30, tags=["raidboss"], other_req_regions=["Terminus"]), "") # voracidous
        | create_rule(world, BL2ArchiData("WingedStorm", 38, tags=["raidboss"]), "") # ancient dragons
        # | create_rule(world, BL2ArchiData("FlamerockRefuge", 30), "") # tina slot machine (insane currently)
    )

# creates a rule for a location, ignores location_data.alternates
def create_rule(world: Borderlands2World, location_data: BL2ArchiData, location_name: str, force_included=False):
    rule = True_()

    if not force_included and not world.is_location_alt_included(location_data, location_name):
        # mark this alternate impossible
        return False_()

    # jump requirement
    if world.options.jump_checks.value > 0:
        if location_data.jump_z_req > 0:
            checks_amt = amt_jump_checks_needed(world, location_data.jump_z_req)
            rule = rule & Has("Progressive Jump", checks_amt)

    # main region requirement
    if location_data.region:
        rule = rule & CanReachRegion(location_data.region)

    # other required regions
    for reg in location_data.other_req_regions:
        rule = rule & CanReachRegion(reg)

    # story required regions (ignored for fully unlocked mode)
    if world.options.fully_unlocked_mode.value == 0:
        for reg in location_data.story_req_regions:
            rule = rule & CanReachRegion(reg)

    # other required items
    for item_name in location_data.req_items:
        if item_name.startswith("License:") and world.is_gear_license_excluded(item_name):
            # skip gear license requirement if setting is off
            continue
        rule = rule & Has(item_name)

    # required item group
    for group in location_data.req_groups:
        rule = rule & HasGroup(group)

    # required rule from rules_dict
    for rule_name in location_data.req_rules:
        extra_rule = world.get_rule(rule_name)
        if extra_rule is None:
            location_data = location_data_table.get(rule_name)
            if not location_data:
                raise RuntimeError("Unknown rule: " + rule_name)
            if world.options.fully_unlocked_mode.value and "story" in location_data.tags:
                # story quest req_rule in fully_unlocked should be ignored 
                extra_rule = True_()
            else:
                extra_rule = create_rule(world, location_data, rule_name, force_included=True)
        rule = rule & extra_rule

    # level requirement
    if location_data.level > 0:
        # with always_on_level on, just add level 1 requirement
        # aol_keep_req means that even if you could kill the enemies, the location requires some amount of progression roughly equal to being that level
        if world.options.always_on_level.value in (1, 2) and not "aol_keep_req" in location_data.tags:
            rule = rule & CanReachLocation("Lvl 1")
        elif location_data.level < 31:
            rule = rule & CanReachLocation(f"Lvl {location_data.level}")
        elif location_data.level >= 31:
            rule = rule & CanReachLocation("Lvl 31")
    return rule


def set_world_rules(world: Borderlands2World):
    setup_level_rules(world)
    setup_custom_rules(world)
    # items must be classified as progression to use in rules here
    menu_region = world.multiworld.get_region("Menu", world.player)
    # rules from location_data_table
    for location_name, location_data in location_data_table.items():
        loc = world.try_get_location(location_name)
        if not loc:
            continue
        rule = create_rule(world, location_data, location_name)
        world.try_add_rule(loc, rule)
        if location_data.alternates:
            for alt_data in location_data.alternates:
                if alt_data.region in world.restricted_regions:
                    # skip if in a restricted region
                    continue
                alt_rule = create_rule(world, alt_data, location_name)
                world.try_add_rule(loc, alt_rule, combine="or")

    # map region connection rules
    if world.options.entrance_locks.value == 1:
        if world.options.fully_unlocked_mode.value:
            for name, region_data in region_data_table.items():
                if name == "Menu":
                    continue
                ent_name = f"Menu to {name}"
                entrance = world.try_get_entrance(ent_name)
                add_travel_item_rule(world, entrance, region_data)
        else:
            for name, region_data in region_data_table.items():
                region = world.multiworld.get_region(name, world.player)
                for c_region_name in region_data.connecting_regions:
                    c_region_data = region_data_table[c_region_name]
                    ent_name = f"{region.name} to {c_region_name}"
                    entrance = world.try_get_entrance(ent_name)

                    # require correct travel item
                    add_travel_item_rule(world, entrance, c_region_data) 

                    # rules for story required regions
                    for story_req_reg_name in c_region_data.story_req_regions:
                        # print(f"{ent_name} - {story_req_reg_name}")
                        world.try_add_rule(entrance, CanReachRegion(story_req_reg_name))
                        # Register indirect condition - required when using regions inside entrance rule
                        # req_region = world.try_get_region(story_req_reg_name)
                        # if req_region:
                        #     world.multiworld.register_indirect_condition(req_region, entrance)
    # misc. region rules

    # challenge requires 10,000
    world.try_add_rule(world.try_get_location("Challenge Money: For the Hoard!"), Has("Progressive Money Cap", 2))

    # SouthernShelf access requires combat
    if world.options.gear_licenses.value > 0:
        world.try_add_rule(world.try_get_entrance("WindshearWaste to SouthernShelf"), CanReachLocation("Lvl 1"))

    # expect player to have access to Backburner before starting FFS
    add_travel_item_rule(world, world.try_get_entrance("Menu to FFSIntroSanctuary"), region_data_table["Backburner"])

    # need melee to get Mordecai blood sample before entering Mt. Scarab Research Center
    world.try_add_rule(world.try_get_entrance("DahlAbandon to Mt.ScarabResearchCenter"), Has("Melee"))

    # need to shoot the bridge halfway through CandlerakksCrag
    if world.options.gear_licenses.value > 0:
        world.try_add_rule(world.try_get_entrance("HuntersGrotto to CandlerakksCrag"), Has("License: Common Pistol"))
        world.try_add_rule(world.try_get_entrance("Menu to CandlerakksCrag"), Has("License: Common Pistol"))

    # Terminus requires crouching through a tunnel. technically there are vending machines before the tunnel, but not gonna worry about it.
    world.try_add_rule(world.try_get_entrance("CandlerakksCrag to Terminus"), Has("Crouch"))
    world.try_add_rule(world.try_get_entrance("Menu to Terminus"), Has("Crouch"))

    # If you die to the dragon, you need to crouch under the gate
    world.try_add_rule(world.try_get_entrance("HatredsShadow to LairOfInfiniteAgony"), Has("Crouch"))

    # Can purchase Seraph Crystals from Earl
    world.try_add_rule(world.try_get_location("Challenge ScarlettDLC: In The Pink"), CanReachRegion("Sanctuary"), combine="or")

    if world.options.jump_checks.value > 0:
        world.try_add_rule(world.try_get_entrance("HerosPass to VaultOfTheWarrior"),
            Has("Progressive Jump", amt_jump_checks_needed(world, 575))) # needed to jump over the broken bridge
        world.try_add_rule(world.try_get_entrance("Menu to VaultOfTheWarrior"),
            Has("Progressive Jump", amt_jump_checks_needed(world, 575))) # needed to jump over the broken bridge

        world.try_add_rule(world.try_get_entrance("LairOfInfiniteAgony to WingedStorm"),
            Has("Progressive Jump", amt_jump_checks_needed(world, 425))) # need to complete Fake Geek Guy
        world.try_add_rule(world.try_get_entrance("Wurmwater to MagnysLighthouse"),
            Has("Progressive Jump", amt_jump_checks_needed(world, 310))) # need to jump onto Magnys Lighthouse dock for all but two checks
        world.try_add_rule(world.try_get_entrance("Menu to MagnysLighthouse"),
            Has("Progressive Jump", amt_jump_checks_needed(world, 310))) # need to jump onto Magnys Lighthouse dock for all but two checks

        world.try_add_rule(world.try_get_entrance("BadassCrater to TorgueArena"),
            Has("Progressive Jump", amt_jump_checks_needed(world, 490))) # jumping out of "kicked out" area, barrier into Badassasaurus fight
        world.try_add_rule(world.try_get_entrance("Menu to TorgueArena"),
            Has("Progressive Jump", amt_jump_checks_needed(world, 490))) # jumping out of "kicked out" area, barrier into Badassasaurus fight

        world.try_add_rule(world.try_get_entrance("Mt.ScarabResearchCenter to FFSBossFight"),
            Has("Progressive Jump", amt_jump_checks_needed(world, 588))) # Almost everything that requires FFS Boss Fight requires completing Paradise Found, which needs 588 jump.
        world.try_add_rule(world.try_get_entrance("Menu to FFSBossFight"),
            Has("Progressive Jump", amt_jump_checks_needed(world, 588))) # Almost everything that requires FFS Boss Fight requires completing Paradise Found, which needs 588 jump.

    # gear reward grants gear location (alternative requirement, use combine="or")
    # TODO: I think this only works for the Progression items (not quest rewards), maybe just remove this
    gear_to_rewards = {}
    for quest_name, data in quest_data_table.items():
        if not data.associated_gear:
            continue
        if data.associated_gear not in gear_to_rewards:
            gear_to_rewards[data.associated_gear] = []
        gear_to_rewards[data.associated_gear].append("Reward: " + quest_name)

    for gear_name in gear_data_table:
        # same item grants location, overrides other rules
        if world.options.receive_gear.value != 0:
            world.try_add_rule(world.try_get_location(f"{gear_name} Found"), Has(f"License: {gear_name}"), combine="or")
        # associated reward grants location
        rewards = gear_to_rewards.get(gear_name, [])
        for reward in rewards:
            world.try_add_rule(world.try_get_location(f"{gear_name} Found"), Has(reward), combine="or")
