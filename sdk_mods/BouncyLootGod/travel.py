
from BouncyLootGod.state import get_globals
from mods_base import Game
if Game.get_current().name == "TPS":
    from BouncyLootGod.bl_tps.entrances import entrance_to_req_areas, travel_targets, region_translation_dict, progressive_travel_lookup, progressive_travel_items, progressive_travel_groups
else:
    from BouncyLootGod.bl2.entrances import entrance_to_req_areas, travel_targets, region_translation_dict, progressive_travel_lookup, progressive_travel_items, progressive_travel_groups

def get_translated_map_name(ugly_map_name):
    return region_translation_dict.get(''.join(filter(str.isalnum, ugly_map_name)).lower())

def is_map_skipped(map_name):
    blg = get_globals()
    translated_regions = [get_translated_map_name(x) for x in blg.settings.get("restricted_regions", [])]
    return map_name in translated_regions

def get_filtered_progressive_travel_group(dlc_group):
    if dlc_group not in progressive_travel_lookup:
        return []

    filtered_arr = [x for x in progressive_travel_lookup[dlc_group] if not is_map_skipped(x)]
    return filtered_arr

def can_travel_to_region(map_name):
    blg = get_globals()
    if blg.settings.get("entrance_locks", 0) == 0:
        return True

    if map_name == "Windshear Waste":
        return True

    if is_map_skipped(map_name):
        return True

    if map_name == "Torgue Arena TAS" or map_name == "Torgue Arena Ring":
        map_name = "Torgue Arena"

    progressive_groups =  blg.settings.get("progressive_travel_groups", [])

    # check for progressive item requirement
    for group_name, region_arr in progressive_travel_lookup.items():
        if group_name in progressive_groups and map_name in region_arr:
            filtered_arr = get_filtered_progressive_travel_group(group_name)
            if map_name not in filtered_arr:
                return True
            item_name = progressive_travel_items[group_name]
            num_req = filtered_arr.index(map_name)
            return blg.has_item(item_name, num_req)

    # otherwise, check for regular travel item
    return blg.has_item(f"Travel: {map_name}")

def get_travel_req_string(map_name):
    blg = get_globals()
    if blg.settings.get("entrance_locks", 0) == 0:
        return ""

    if map_name == "Windshear Waste":
        return ""

    if map_name == "Torgue Arena TAS" or map_name == "Torgue Arena Ring":
        map_name = "Torgue Arena"

    progressive_groups =  blg.settings.get("progressive_travel_groups", [])

    # check for progressive item requirement
    for group_name, region_arr in progressive_travel_lookup.items():
        if group_name in progressive_groups and map_name in region_arr:
            filtered_arr = get_filtered_progressive_travel_group(group_name)
            if map_name not in filtered_arr:
                return "(Unavailable)"
            item_name = progressive_travel_items[group_name]
            num_req = filtered_arr.index(map_name)
            return f"{item_name} * {num_req}"

    # otherwise, check for regular travel item
    return f"Travel: {map_name}"

def get_newly_unlocked_region_name(item_name, amt):
    group = progressive_travel_groups[item_name]
    arr = get_filtered_progressive_travel_group(group)
    if amt >= len(arr):
        return ""
    return arr[amt]

def get_entrance_lock_warnings(map_name):
    exit_areas = set()
    for areas in entrance_to_req_areas.values():
        if len(areas) > 0 and areas[0] == map_name:
            exit_areas.update(areas)
    warning_areas = []
    for a in exit_areas:
        if not can_travel_to_region(a):
            warning_areas.append(a)
    return warning_areas
