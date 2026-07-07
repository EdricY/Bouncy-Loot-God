import unrealsdk
from unrealsdk.hooks import Type
import unrealsdk.unreal as unreal
from BouncyLootGod.enemies import setup_check_drop, oid_generic_drop_chance_override
from BouncyLootGod.state import get_globals
from BouncyLootGod.networking import push_locations
from BouncyLootGod.bl_tps.enemies import generic_enemy_lookup
from BouncyLootGod.archi_data import loc_name_to_id
from mods_base import ENGINE


def get_current_map():
    if ENGINE and ENGINE.GetCurrentWorldInfo:
        wi = ENGINE.GetCurrentWorldInfo()
        if wi and wi.GetMapName:
            return str(wi.GetMapName()).casefold()
    return "none"
def modify_veins_of_helios():
    unrealsdk.load_package("Innerhull_Combat") #explisitly load the combat package, as the game loads it after spawning
    
def modify_vorago_solitude():
    #todo: fix zealots
    pass
def modify_tychos_ribs():
    #todo: fix zealots
    pass
def modify_digsite_rk5arena():
    loc_name = "Enemy: Raum-Kampfjet Mark V"
    loc_id = loc_name_to_id.get(loc_name)
    if loc_id is None:
        return
    blg = get_globals()
    def fix_rk5_event(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
        if get_current_map() != "digsite_rk5arena_p":
            print("Removing rk5 hook")
            unrealsdk.hooks.remove_hook("GearboxFramework.Behavior_CustomEvent:ApplyBehaviorToContext", Type.PRE, "fix_rk5_event")
            return
        if obj.CustomEventName != "NowInDeathPosition":
            return
        if loc_id not in blg.locations_checked and loc_id not in blg.locs_to_send:
            blg.locs_to_send.append(loc_id)
            push_locations()
            print("Removing rk5 hook")
            unrealsdk.hooks.remove_hook("GearboxFramework.Behavior_CustomEvent:ApplyBehaviorToContext", Type.PRE, "fix_rk5_event")
    unrealsdk.hooks.add_hook(
        "GearboxFramework.Behavior_CustomEvent:ApplyBehaviorToContext",
        Type.PRE,
        "fix_rk5_event",
        fix_rk5_event
    )
def modify_triton_flats():
    unrealsdk.hooks.add_hook(
        "WillowGame.VehicleClassDefinition:ProcessSeatEvent",
        Type.POST,
        "modify_triton_flats_vehicle_drivers",
        modify_triton_flats_vehicle_drivers
    )
def modify_triton_flats_vehicle_drivers(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if get_current_map() != "moon_p":
        print("Removing triton flats hook")
        unrealsdk.hooks.remove_hook("WillowGame.VehicleClassDefinition:ProcessSeatEvent", Type.POST, "modify_triton_flats_vehicle_drivers")
        return
    driver=getattr(args, "Occupant")
    """
    The game spawns a vehicle in a way i do not know,
    then spawns a pawn,
    then seats that pawn in the vehicle.
    it is at this point we inject our lootpool changes, as we can listen to this event
    and locate the runtime vehicle object and append our check item to its pool
    """
    if not driver:
        return
    #ensure pawn is driving aka not exited (somehow), is not the player, and the pawn is not "driving" the vehicle weapon 
    if not driver.DrivenVehicle or driver.Class.Name != "WillowAIPawn"  or driver.DrivenVehicle.Class.Name != "WillowVehicle_WheeledVehicle":
        return
    blg = get_globals()
    skip_already_checked=True
    if oid_generic_drop_chance_override.value != 0:
        chance = oid_generic_drop_chance_override.value / 100
        skip_already_checked=False
    else:
        chance = blg.settings.get("generic_mob_checks", 5) * 0.01
    if "buggy" in driver.DrivenVehicle.ChassisDef.Name.lower():
        setup_check_drop("Generic: Vehicle", behavior_spawn_items=driver.DrivenVehicle, chance=chance, skip_already_checked=skip_already_checked)
def modify_claptrap_pandora():
    fix_claptrap_dlc_enemies()
def modify_claptrap_motherboard():
    fix_claptrap_dlc_enemies()
def modify_claptrap_overlook():
    fix_claptrap_dlc_enemies()
def modify_claptrap_subconcious():
    fix_claptrap_dlc_enemies()
def modify_claptrap_cortex():
    fix_claptrap_dlc_enemies()
def fix_claptrap_dlc_enemies():
    """
    Claptrap DLC enemies can spawn while ignoring the AIPawnBalanceDefinition DefaultItemPoolList
    so we watch spawns happening in the regions and sync the lootpools for this mod again
    there is likely a better way to address this, but found no obvious flags or entryways to achieve this
    """
    blg = get_globals()

    if blg.settings.get("generic_mob_checks", 0) == 0:
        return
    unrealsdk.hooks.add_hook(
        "WillowGame.PopulationFactoryBalancedAIPawn:SpawnAIPawn",
        Type.POST,
        "hook_spawn_ai_pawn_to_fix_dlc_enemies",
        hook_spawn_ai_pawn_to_fix_dlc_enemies
    )
broken_maps = ["ma_leftcluster_p","ma_rightcluster_p","ma_motherboard_p","ma_leftcluster_p","ma_subconscious_p","ma_subboss_p"]
def hook_spawn_ai_pawn_to_fix_dlc_enemies(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    skip_already_checked=True
    if oid_generic_drop_chance_override.value != 0:
        chance = oid_generic_drop_chance_override.value / 100
        skip_already_checked=False
    else:
        chance = blg.settings.get("generic_mob_checks", 5) * 0.01
    map_name=get_current_map()
    if map_name not in broken_maps: #remove the hook if the current map is not one of the DLC maps that contain broken APBD's
        unrealsdk.hooks.remove_hook("WillowGame.PopulationFactoryBalancedAIPawn:SpawnAIPawn", Type.POST, "hook_spawn_ai_pawn_to_fix_dlc_enemies")
        print("Uninstalled hook: hook_spawn_ai_pawn_to_fix_dlc_enemies")
        return
    pawn_def = getattr(ret.BalanceDefinitionState, "BalanceDefinition")
    #cross check AIPawn with APBD ItemPoolList and re-add any AP pools the AIPawn is missing
    for pool in pawn_def.DefaultItemPoolList:
        pool_name = pool.ItemPool.Name
        if ("archi_pool_" not in pool_name
                or any(pawn_pool.ItemPool.Name == pool_name for pawn_pool in ret.ItemPoolList)):
            continue
        check_name = pool_name.lstrip("_archi_pool_")
        pawn_str = str(pawn_def).lower()
        if pawn_def.Champion:
            setup_check_drop(check_name, behavior_spawn_items=ret, chance=chance, skip_already_checked=skip_already_checked)
        else:
            for search_str, generic_enemy in generic_enemy_lookup.items():
                if generic_enemy != check_name:
                    continue
                if pawn_def and search_str in pawn_str:
                    setup_check_drop(generic_enemy, behavior_spawn_items=ret, chance=chance, skip_already_checked=skip_already_checked)

map_modifications = {
    "innerhull_p": modify_veins_of_helios,
    "digsite_p": modify_vorago_solitude,
    "access_p": modify_tychos_ribs,
    "digsite_rk5arena_p": modify_digsite_rk5arena,
    "moon_p": modify_triton_flats,
    "ma_leftcluster_p": modify_claptrap_pandora,
    "ma_rightcluster_p": modify_claptrap_overlook,
    "ma_motherboard_p": modify_claptrap_motherboard,
    "ma_subconscious_p": modify_claptrap_subconcious,
    "ma_subboss_p": modify_claptrap_cortex,
}

map_area_to_name = {
    "moonslaughter_p":          "Abandoned Training Facility",
    "ma_leftcluster_p":         "Cluster 00773 P4ND0R4",
    "ma_rightcluster_p":        "Cluster 99002 0V3RL00K",
    "spaceport_p":              "Concordia",
    "comfacility_p":            "Crisis Scar",
    "ma_deck13_p":              "Deck 13 ½",
    "ma_finalboss_p":           "EOSArena",
    "innercore_p":              "Eleseer",
    "laserboss_p":              "Eye of Helios",
    "moonshotintro_p":          "Helios Station",
    "centralterminal_p":        "Hyperion Hub of Heroism",
    "jacksoffice_p":            "Jack's Office",
    "laser_p":                  "Lunar Launching Station",
    "ma_motherboard_p":         "Motherlessboard",
    "digsite_rk5arena_p":       "Outfall Pumping Station",
    "outlands_p2":              "Outlands Canyon",
    "outlands_p":               "Outlands Spur",
    "wreck_p":                  "Pity's Fall",
    "deadsurface_p":            "Regolith Range",
    "randdfacility_p":          "Research and Development",
    "moonsurface_p":            "Serenity's Waste",
    "stantonsliver_p":          "Stanton's Liver",
    "sublevel13_p":             "Sub-Level 13",
    "ma_subconscious_p":        "Subconscious",
    "ma_subboss_p":             "The Cortex",
    "eridian_slaughter_p":      "The Holodome",
    "meriff_p":                 "The Meriff's Office",
    "ma_nexus_p":               "The Nexus",
    "dahlfactory_p":            "Titan Industrial Facility",
    "dahlfactory_boss":         "Titan Robot Production Plant",
    "moon_p":                   "Triton Flats",
    "access_p":                 "Tycho's Ribs",
    "innerhull_p":              "Veins of Helios",
    "digsite_p":                "Vorago Solitude",
}
