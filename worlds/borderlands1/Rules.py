from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Borderlands1World
from math import sqrt
from worlds.generic.Rules import set_rule, add_rule

from .Regions import region_data_table, progressive_travel_items, progressive_travel_dict
from .Locations import Borderlands1Location, location_data_table
from .Items import Borderlands1Item
from .archi_defs import gear_data_table, quest_data_table, BL1ArchiData
from BaseClasses import ItemClassification, Region


def try_add_rule(place, rule, combine="and"):
    if place is None:
        return
    try:
        add_rule(place, rule, combine)
    except:
        print(f"failed setting rule at {place}")


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
        try_add_rule(entrance, lambda state, item_name=p_t_item_name, checks_amt=amt: state.has(item_name, world.player, checks_amt))
    
    else:
        try_add_rule(entrance, lambda state, item_name=t_item_name: state.has(item_name, world.player))

def and_rule(rule1, rule2):
    return lambda state: rule1(state) and rule2(state)

def or_rule(rule1, rule2):
    return lambda state: rule1(state) or rule2(state)

# creates a rule for a location, ignores location_data.alternates
def create_rule(world: Borderlands1World, location_data: BL1ArchiData, location_name: str):
    rule = lambda state: True

    if not world.is_location_alt_included(location_data, location_name):
        # mark this alternate impossible
        return lambda state: False

    # jump requirement
    if world.options.jump_checks.value > 0:
        if location_data.jump_z_req > 0:
            checks_amt = amt_jump_checks_needed(world, location_data.jump_z_req)
            rule = and_rule(rule, lambda state, checks_amt=checks_amt: state.has("Progressive Jump", world.player, checks_amt))

    # main region requirement
    if location_data.region:
        rule = and_rule(rule, lambda state, region=location_data.region: state.can_reach_region(region, world.player))

    # other required regions
    for reg in location_data.other_req_regions:
        rule = and_rule(rule, lambda state, region=reg: state.can_reach_region(region, world.player))

    # other required items
    for item_name in location_data.req_items:
        if item_name.startswith("License:") and world.is_gear_license_excluded(item_name):
            # skip gear license requirement if setting is off
            continue
        rule = and_rule(rule, lambda state, item_name=item_name: state.has(item_name, world.player))

    # required item group
    for group in location_data.req_groups:
        rule = and_rule(rule, lambda state, group=group: state.has_group(group, world.player))

    # level requirement
    if location_data.level > 0:
        # always_on_level on, just add level 1 requirement
        # aol_keep_req means that even if you could kill the enemies, the location requires some amount of progression roughly equal to being that level
        if world.options.always_on_level.value in (1, 2) and not "aol_keep_req" in location_data.tags:
            rule = and_rule(rule, lambda state, lvl=location_data.level: state.has(f"Lvl 1", world.player))
        elif location_data.level < 31:
            rule = and_rule(rule, lambda state, lvl=location_data.level: state.has(f"Lvl {lvl}", world.player))
        elif location_data.level >= 31:
            rule = and_rule(rule, lambda state: state.has(f"Lvl 31", world.player))
    return rule


def set_world_rules(world: Borderlands1World):

    # items must be classified as progression to use in rules here
    menu_region = world.multiworld.get_region("Menu", world.player)
    # rules from location_data_table
    for location_name, location_data in location_data_table.items():
        loc = world.try_get_location(location_name)
        if not loc:
            continue
        rule = create_rule(world, location_data, location_name)
        try_add_rule(loc, rule)
        if location_data.alternates:
            for alt_data in location_data.alternates:
                if alt_data.region in world.restricted_regions:
                    # skip if in a restricted region
                    continue
                alt_rule = create_rule(world, alt_data, location_name)
                try_add_rule(loc, alt_rule, combine="or")

    # map region connection rules
    if world.options.entrance_locks.value == 1:
        for name, region_data in region_data_table.items():
            region = world.multiworld.get_region(name, world.player)
            for c_region_name in region_data.connecting_regions:
                c_region_data = region_data_table[c_region_name]
                ent_name = f"{region.name} to {c_region_name}"
                t_item = c_region_data.travel_item_name
                entrance = world.try_get_entrance(ent_name)

                # require correct travel item
                add_travel_item_rule(world, entrance, c_region_data) 

                # rules for story required regions
                for story_req_reg_name in c_region_data.story_req_regions:
                    # print(f"{ent_name} - {story_req_reg_name}")
                    try_add_rule(entrance, lambda state, reg=story_req_reg_name: state.can_reach_region(reg, world.player))
                    # Register indirect condition - required when using regions inside entrance rule
                    req_region = world.try_get_region(story_req_reg_name)
                    if req_region:
                        world.multiworld.register_indirect_condition(req_region, entrance)

    for lvl in range(1, 32): # 1 to 31
        ev_name = f"Lvl {lvl}"
        (ev, loc) = world.create_event_at(ev_name, "Menu")
        loc.show_in_spoiler = False
        # go through regions, require at least one that has this lvl
        rule = lambda state: False
        for region_name, region_data in region_data_table.items():
            if region_data.min_level < lvl and region_data.max_level >= lvl:
                rule = or_rule(rule, lambda state, region_name=region_name: state.can_reach_region(region_name, world.player))
        # require previous level
        if lvl > 1:
            prev_lvl = lvl-1
            rule = and_rule(rule, lambda state, prev_lvl=prev_lvl: state.has(f"Lvl {prev_lvl}", world.player))
        try_add_rule(loc, rule)

    if world.options.gear_licenses.value > 0:
        # require basic combat to surpass level 0
        try_add_rule(world.try_get_location("Lvl 1"), lambda state: state.has_any(["Melee", "License: Common Pistol"], world.player))
        # require reasonable loadout to surpass level 10
        try_add_rule(world.try_get_location("Lvl 10"), lambda state: state.has_all(["Melee", "License: Common Pistol", "License: Common Shield", "License: Common Shotgun", "License: Uncommon Pistol"], world.player))

    # misc. region rules

    # challenge requires 10,000
    try_add_rule(world.try_get_location("Challenge Money: For the Hoard!"), 
        lambda state: state.has("Progressive Money Cap", world.player, 2))

    # SouthernShelf access requires combat
    if world.options.gear_licenses.value > 0:
        try_add_rule(world.try_get_entrance("WindshearWaste to SouthernShelf"), lambda state: state.has("Lvl 1", world.player))

    # expect player to have access to Backburner before starting FFS
    add_travel_item_rule(world, world.try_get_entrance("Menu to FFSIntroSanctuary"), region_data_table["Backburner"])

    # need melee to get Mordecai blood sample before entering Mt. Scarab Research Center
    try_add_rule(world.try_get_entrance("DahlAbandon to Mt.ScarabResearchCenter"),
             lambda state: state.has("Melee", world.player))

    # need to shoot the bridge halfway through CandlerakksCrag
    try_add_rule(world.try_get_entrance("HuntersGrotto to CandlerakksCrag"),
        lambda state: state.has("License: Common Pistol", world.player))

    # Terminus requires crouching through a tunnel. technically there are vending machines before the tunnel, but not gonna worry about it.
    try_add_rule(world.try_get_entrance("CandlerakksCrag to Terminus"),
        lambda state: state.has("Crouch", world.player))

    # If you die to the dragon, you need to crouch under the gate
    try_add_rule(world.try_get_entrance("HatredsShadow to LairOfInfiniteAgony"),
             lambda state: state.has("Crouch", world.player))

    # Can purchase Seraph Crystals from Earl
    try_add_rule(world.try_get_location("Challenge ScarlettDLC: In The Pink"), 
        lambda state: state.can_reach_region("Sanctuary", world.player), combine="or")

    if world.options.jump_checks.value > 0:
        try_add_rule(world.try_get_entrance("BadassCrater to TorgueArena"),
            lambda state: state.has("Progressive Jump", world.player, amt_jump_checks_needed(world, 490))) # jumping out of "kicked out" area, final cookie vending machine, barrier into Badassasaurus fight
        try_add_rule(world.try_get_entrance("HerosPass to VaultOfTheWarrior"),
            lambda state: state.has("Progressive Jump", world.player, amt_jump_checks_needed(world, 575))) # needed to jump over the broken bridge
        try_add_rule(world.try_get_entrance("Mt.ScarabResearchCenter to FFSBossFight"),
            lambda state: state.has("Progressive Jump", world.player, amt_jump_checks_needed(world, 588))) # Almost everything that requires FFS Boss Fight requires completing Paradise Found, which needs 588 jump.  
        try_add_rule(world.try_get_entrance("LairOfInfiniteAgony to WingedStorm"),
            lambda state: state.has("Progressive Jump", world.player, amt_jump_checks_needed(world, 425))) # need to complete Fake Geek Guy
        try_add_rule(world.try_get_entrance("Wurmwater to MagnysLighthouse"),
            lambda state: state.has("Progressive Jump", world.player, amt_jump_checks_needed(world, 310))) # need to jump onto Magnys Lighthouse dock for all but two checks
        try_add_rule(world.try_get_entrance("BadassCrater to SouthernRaceway"),
            lambda state: state.has("Progressive Jump", world.player, amt_jump_checks_needed(world, 450))) # need to complete Eat Cookies and Crap Thunder      
        try_add_rule(world.try_get_entrance("BadassCrater to BadassCraterBar"),
            lambda state: state.has("Progressive Jump", world.player, amt_jump_checks_needed(world, 395))) # need to rescue Moxxi      


    # TODO: these events should be removed/skipped if inaccesssible. Could move to archi_defs file, or maybe recreated as rules in a Rule Builder refactor
    # detecting end of Torgue DLC is a little weird.
    if "Forge" not in world.restricted_regions:
        (event, loc) = world.create_event_at("Torgue DLC Complete", "TorgueArena")
        try_add_rule(loc, lambda state: state.can_reach_region("Forge", world.player))
        try_add_rule(loc, lambda state: state.has("Progressive Jump", world.player, amt_jump_checks_needed(world, 546)))
        try_add_rule(loc, lambda state: state.has("Crouch", world.player))

        # can farm torgue tokens (we'll say death race for now)
        (event, loc) = world.create_event_at("Torgue Tokens Accessible", "BadassCrater")
        try_add_rule(loc, create_rule(world, BL1ArchiData("BadassCraterBar", 15), ""))

    # can farm seraph crystals (not all raidbosses drop them)
    (event, loc) = world.create_event_at("Seraph Crystals Accessible", "Menu")
    try_add_rule(loc, lambda state: state.can_reach_region("Sanctuary", world.player)) # from black market
    try_add_rule(loc, create_rule(world, BL1ArchiData("WashburneRefinery", 30, tags=["raidboss"], other_req_regions=["LeviathansLair"]), ""), combine="or") # hyperius
    try_add_rule(loc, create_rule(world, BL1ArchiData("HaytersFolly", 30, tags=["raidboss"], other_req_regions=["LeviathansLair"]), ""), combine="or") # gee
    try_add_rule(loc, create_rule(world, BL1ArchiData("PyroPetesBar", 30, req_items=["Torgue DLC Complete"], tags=["raidboss"]), ""), combine="or") # pete
    try_add_rule(loc, create_rule(world, BL1ArchiData("CandlerakksCrag", 30, tags=["raidboss"], other_req_regions=["Terminus"]), ""), combine="or") # voracidous
    try_add_rule(loc, create_rule(world, BL1ArchiData("WingedStorm", 38, tags=["raidboss"]), ""), combine="or") # ancient dragons
    # try_add_rule(loc, create_rule(world, BL1ArchiData("FlamerockRefuge", 30), ""), combine="or") # slot machine (insane currently)


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
            try_add_rule(world.try_get_location(f"{gear_name} Found"), lambda state, gear_item=f"License: {gear_name}": state.has(gear_item, world.player), combine="or")
        # associated reward grants location
        rewards = gear_to_rewards.get(gear_name, [])
        for reward in rewards:
            try_add_rule(world.try_get_location(f"{gear_name} Found"), lambda state, r=reward: state.has(r, world.player), combine="or")

    # alternative override for levels
    for lvl in range(1, 16):
        try_add_rule(world.try_get_location(f"Lvl {lvl}"), lambda state: state.has("Override Level 15", world.player), combine="or")
    for lvl in range(1, 31):
        try_add_rule(world.try_get_location(f"Lvl {lvl}"), lambda state: state.has("Override Level 30", world.player), combine="or")
