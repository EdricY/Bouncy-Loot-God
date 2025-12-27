from math import sqrt
from worlds.generic.Rules import set_rule, add_rule

from . import Borderlands2World
from .Regions import region_data_table
from .Locations import Borderlands2Location, location_data_table
from BaseClasses import ItemClassification

def try_add_rule(place, rule):
    if place is None:
        return
    try:
        add_rule(place, rule)
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


def set_rules(world: Borderlands2World):

    # items must be classified as progression to use in rules here
    try_add_rule(world.try_get_entrance("WindshearWaste to SouthernShelf"),
        lambda state: state.has("Melee", world.player) and state.has("Common Pistol", world.player))
    #add_rule(world.multiworld.get
    # add_rule(world.multiworld.get_entrance("SouthernShelf to ThreeHornsDivide", world.player),
    #     lambda state: state.has("Common Pistol", world.player))
    # add_rule(world.multiworld.get_location("Enemy WindshearWaste: Knuckle Dragger", world.player),
    #     lambda state: state.has("Melee", world.player))

    if world.options.jump_checks.value > 0:
        # ensure you can at least jump a little before wildlife preserve
        # try_add_rule(world.try_get_entrance("Highlands to WildlifeExploitationPreserve"),
        #     lambda state: state.has("Progressive Jump", world.player))
        try_add_rule(world.try_get_entrance("HerosPass to VaultOfTheWarrior"),
            lambda state: state.has("Progressive Jump", world.player))
        try_add_rule(world.try_get_entrance("BadassCrater to TorgueArena"), # 490 jump_z required
            lambda state: state.has("Progressive Jump", world.player))
        try_add_rule(world.try_get_entrance("BloodshotRamparts to Oasis"),
                 lambda state: state.has("Progressive Jump", world.player))

    try_add_rule(world.try_get_location("Challenge Vehicles: Turret Syndrome"),
        lambda state: state.has("Vehicle Fire", world.player))

    #need melee to break vines to Hector
    try_add_rule(world.try_get_entrance("Mt.ScarabResearchCenter to FFSBossFight"),
             lambda state: state.has("Melee", world.player))

    try_add_rule(world.try_get_entrance("CandlerakksCrag to Terminus"),
            lambda state: state.has("Crouch", world.player))
    # If you die to the dragon, you need to crouch under the gate
    try_add_rule(world.try_get_entrance("HatredsShadow to LairOfInfiniteAgony"),
             lambda state: state.has("Crouch", world.player))

    # FFS Butt Stalion requires the amulet
    try_add_rule(world.try_get_location("Challenge Backburner: Fandir Fiction"),
            lambda state: state.has("Unique Relic", world.player))
    try_add_rule(world.try_get_location("Challenge Backburner: Fandir Fiction"),
            lambda state: state.has("Reward Agony: The Amulet", world.player))
    try_add_rule(world.try_get_location("Rainbow Shotgun"),
            lambda state: state.has("Unique Relic", world.player))
    try_add_rule(world.try_get_location("Rainbow Shotgun"),
            lambda state: state.has("Reward Agony: The Amulet", world.player))

    try_add_rule(world.try_get_location("Challenge Sanctuary: Jackpot!"),
            lambda state: state.has("Progressive Money Cap", world.player))
    

    for location_name, location_data in location_data_table.items():
        if location_data.crouch_req:
            try_add_rule(world.try_get_location(location_name),
                lambda state: state.has("Crouch", world.player)
            )

        if world.options.jump_checks.value > 0:
            if location_data.jump_z_req > 0:
                checks_amt = amt_jump_checks_needed(world, location_data.jump_z_req)
                print(f"jump_z_req {location_data.jump_z_req} checks: {checks_amt}")
                try_add_rule(world.try_get_location(location_name),
                    lambda state, checks_amt=checks_amt: state.has("Progressive Jump", world.player, checks_amt)
                )
        
        for reg in location_data.other_req_regions:
            try_add_rule(world.try_get_location(location_name),
                lambda state, region=reg: state.can_reach_region(region, world.player)
            )

        for group in location_data.req_groups:
            try_add_rule(world.try_get_location(location_name),
                lambda state, group=group: state.has_group(group, world.player)
            )


    # TODO: level regions and can_reach rules

    # region connection rules
    if world.options.entrance_locks.value == 1:
        for name, region_data in region_data_table.items():
            region = world.multiworld.get_region(name, world.player)
            for c_region_name in region_data.connecting_regions:
                c_region_data = region_data_table[c_region_name]
                ent_name = f"{region.name} to {c_region_name}"
                t_item = c_region_data.travel_item_name
                if t_item and isinstance(t_item, str):
                    try_add_rule(
                        world.try_get_entrance(ent_name),
                        lambda state, travel_item=t_item: state.has(travel_item, world.player)
                    )
                elif t_item and isinstance(t_item, list):
                    try_add_rule(
                        world.try_get_entrance(ent_name),
                        lambda state, travel_item=t_item: state.has_all(travel_item, world.player)
                    )



