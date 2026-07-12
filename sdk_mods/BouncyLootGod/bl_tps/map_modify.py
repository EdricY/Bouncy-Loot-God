import unrealsdk
from BouncyLootGod.bl_tps.chests import chest_dict
from unrealsdk.hooks import Type
import unrealsdk.unreal as unreal
from BouncyLootGod.enemies import setup_check_drop, oid_generic_drop_chance_override
from BouncyLootGod.loot_pools import create_modified_item_pool
from BouncyLootGod.state import get_globals, get_or_create_package
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


def modify_moonshot_intro():
    blg = get_globals()
    if blg.settings.get("delete_starting_gear") == 1:
        # make the loyalty pools empty to prevent giving the items
        try:
            loyalty_bullpup_pool = unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.EasterEggs.Pool_Loyalty_Bullpup")
            loyalty_bullpup_pool.BalancedItems = []
        except:
            pass
        try:
            loyalty_smasher_pool = unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.EasterEggs.Pool_Loyalty_Smasher")
            loyalty_smasher_pool.BalancedItems = []
        except:
            pass


def modify_veins_of_helios():
    unrealsdk.load_package("Innerhull_Combat")  # explisitly load the combat package, as the game loads it after spawning
    dan = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Cork_DontGetCocky_Data.Balance.PawnBalance_DanZando")

    item_pool = unrealsdk.construct_object("ItemPoolDefinition", get_or_create_package(), "BLG_TPS_Dan_Zaldo")
    inv_bal_def_name = "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Old_Hyperion_3_Bullpup"
    inv_bal_def = unrealsdk.find_object("InventoryBalanceDefinition", inv_bal_def_name)
    # the creamer is already min level on its parts, so we dont really need to worry about the cleanup funcs
    probability = unrealsdk.make_struct(
        "AttributeInitializationData",
        BaseValueConstant=1,
        BaseValueAttribute=None,
        InitializationDefinition=None,
        BaseValueScaleConstant=1.000000
    )
    balanced_item = unrealsdk.make_struct("BalancedInventoryData", InvBalanceDefinition=inv_bal_def, Probability=probability, bDropOnDeath=True)
    item_pool.BalancedItems.append(balanced_item)
    item_pool_info = unrealsdk.make_struct(
        "ItemPoolInfo",
        ItemPool=item_pool,
        PoolProbability=probability
    )
    dan.DefaultItemPoolList.append(item_pool_info)


def modify_vorago_solitude():
    zealot_drop_pool()
    ai_class = "GD_Co_NPCs_GuardianHunter.Character.CharClass_ScavBandit"
    pwns = unrealsdk.find_all("WillowAIPawn")
    for pawn in pwns:
        if ai_class not in str(pawn.AIClass):
            continue
        pawn_def = unrealsdk.construct_object("AIPawnBalanceDefinition", get_or_create_package(), "PawnDef_MasterPoacher", 0, None)
        pawn.BalanceDefinitionState.BalanceDefinition = pawn_def


def modify_eridian_slaughter():
    zealot_drop_pool()


def modify_tychos_ribs():
    zealot_drop_pool()


def zealot_drop_pool():
    loc_name = "Generic: Lost Legion"
    loc_id = loc_name_to_id.get(loc_name)
    if loc_id is None:
        return
    blg = get_globals()

    def fix_zealot_itempool(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
        if get_current_map() not in ["digsite_p", "access_p", "eridian_slaughter_p"]:
            print("Removing zealot hook")
            unrealsdk.hooks.remove_hook("GearboxFramework.Behavior_CustomEvent:ApplyBehaviorToContext", Type.PRE, "fix_zealot_itempool")
            return
        pawn = getattr(args, "ContextObject", None)
        obj_identifier = str(obj).lower()
        event_name = obj.CustomEventName.lower()
        if not pawn or event_name not in ["announceconversion"] or "eternal" not in obj_identifier:
            return
        for pool in pawn.ItemPoolList:
            if loc_name in pool.Name:
                return
        skip_already_checked = True
        if oid_generic_drop_chance_override.value != 0:
            chance = oid_generic_drop_chance_override.value / 100
            skip_already_checked = False
        else:
            chance = blg.settings.get("generic_mob_checks", 5) * 0.01
        setup_check_drop(loc_name, behavior_spawn_items=pawn, chance=chance, skip_already_checked=skip_already_checked)

    unrealsdk.hooks.add_hook(
        "GearboxFramework.Behavior_CustomEvent:ApplyBehaviorToContext",
        Type.PRE,
        "fix_zealot_itempool",
        fix_zealot_itempool
    )


def modify_randdfacility():
    blg = get_globals()

    def pet_benjamin_listener(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
        map_area = get_current_map()
        if map_area != "randdfacility_p":
            print("Removing BB hook")
            unrealsdk.hooks.remove_hook("WillowGame.WillowInteractiveObject:UseObject", Type.PRE, "pet_benjamin_listener")
            return
        location = f"{map_area}~{int(obj.Location.X)},{int(obj.Location.Y)}"
        loc_name = chest_dict.get(location)
        print(f"{location}: {loc_name} @ {str(obj)}")
        if not loc_name or not loc_name.startswith("Special: "):
            return
        loc_id = loc_name_to_id.get(loc_name)
        if not loc_id:
            return
        if loc_id not in blg.locations_checked and loc_id not in blg.locs_to_send:
            blg.locs_to_send.append(loc_id)
            push_locations()
            print("Removing BB hook")
            unrealsdk.hooks.remove_hook("WillowGame.WillowInteractiveObject:UseObject", Type.PRE, "pet_benjamin_listener")
            print("installing pet_benjamin_listener hook")
    unrealsdk.hooks.add_hook(
        "WillowGame.WillowInteractiveObject:UseObject",
        Type.PRE,
        "pet_benjamin_listener",
        pet_benjamin_listener
    )


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
    oscar = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Scavengers.Balance.Psychos.PawnBalance_ScavSuicidePsycho_Oscar")

    item_pool = unrealsdk.construct_object("ItemPoolDefinition", get_or_create_package(), "BLG_TPS_Oscar")
    inv_bal_def_name = "GD_Cork_Weap_Launchers.A_Weapons_Unique.RL_Torgue_3_Creame"
    inv_bal_def = unrealsdk.find_object("InventoryBalanceDefinition", inv_bal_def_name)
    # the creamer is already min level on its parts, so we dont really need to worry about the cleanup funcs
    probability = unrealsdk.make_struct(
        "AttributeInitializationData",
        BaseValueConstant=0.15,
        BaseValueAttribute=None,
        InitializationDefinition=None,
        BaseValueScaleConstant=1.000000
    )
    balanced_item = unrealsdk.make_struct("BalancedInventoryData", InvBalanceDefinition=inv_bal_def, Probability=probability, bDropOnDeath=True)
    item_pool.BalancedItems.append(balanced_item)
    item_pool_info = unrealsdk.make_struct(
        "ItemPoolInfo",
        ItemPool=item_pool,
        PoolProbability=probability
    )
    oscar.DefaultItemPoolList.append(item_pool_info)
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
    driver = getattr(args, "Occupant")
    """
    The game spawns a vehicle in a way i do not know,
    then spawns a pawn,
    then seats that pawn in the vehicle.
    it is at this point we inject our lootpool changes, as we can listen to this event
    and locate the runtime vehicle object and append our check item to its pool
    """
    if not driver:
        return
    # ensure pawn is driving aka not exited (somehow), is not the player, and the pawn is not "driving" the vehicle weapon 
    if not driver.DrivenVehicle or driver.Class.Name != "WillowAIPawn" or driver.DrivenVehicle.Class.Name != "WillowVehicle_WheeledVehicle":
        return
    blg = get_globals()
    skip_already_checked = True
    if oid_generic_drop_chance_override.value != 0:
        chance = oid_generic_drop_chance_override.value / 100
        skip_already_checked = False
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


broken_maps = ["ma_leftcluster_p", "ma_rightcluster_p", "ma_motherboard_p", "ma_leftcluster_p", "ma_subconscious_p", "ma_subboss_p"]


def hook_spawn_ai_pawn_to_fix_dlc_enemies(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    blg = get_globals()
    skip_already_checked = True
    if oid_generic_drop_chance_override.value != 0:
        chance = oid_generic_drop_chance_override.value / 100
        skip_already_checked = False
    else:
        chance = blg.settings.get("generic_mob_checks", 5) * 0.01
    map_name = get_current_map()
    if map_name not in broken_maps:  # remove the hook if the current map is not one of the DLC maps that contain broken APBD's
        unrealsdk.hooks.remove_hook("WillowGame.PopulationFactoryBalancedAIPawn:SpawnAIPawn", Type.POST, "hook_spawn_ai_pawn_to_fix_dlc_enemies")
        print("Uninstalled hook: hook_spawn_ai_pawn_to_fix_dlc_enemies")
        return
    pawn_def = getattr(ret.BalanceDefinitionState, "BalanceDefinition")
    # cross check AIPawn with APBD ItemPoolList and re-add any AP pools the AIPawn is missing
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
    "moonshotintro_p": modify_moonshot_intro,
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
    "eridian_slaughter_p": modify_eridian_slaughter,
    "randdfacility_p": modify_randdfacility,
}

map_area_to_name = {
    "moonslaughter_p": "Abandoned Training Facility",
    "ma_leftcluster_p": "Cluster 00773 P4ND0R4",
    "ma_rightcluster_p": "Cluster 99002 0V3RL00K",
    "spaceport_p": "Concordia",
    "comfacility_p": "Crisis Scar",
    "ma_deck13_p": "Deck 13 ½",
    "ma_finalboss_p": "EOSArena",
    "innercore_p": "Eleseer",
    "laserboss_p": "Eye of Helios",
    "moonshotintro_p": "Helios Station",
    "centralterminal_p": "Hyperion Hub of Heroism",
    "jacksoffice_p": "Jack's Office",
    "laser_p": "Lunar Launching Station",
    "ma_motherboard_p": "Motherlessboard",
    "digsite_rk5arena_p": "Outfall Pumping Station",
    "outlands_p2": "Outlands Canyon",
    "outlands_p": "Outlands Spur",
    "wreck_p": "Pity's Fall",
    "deadsurface_p": "Regolith Range",
    "randdfacility_p": "Research and Development",
    "moonsurface_p": "Serenity's Waste",
    "stantonsliver_p": "Stanton's Liver",
    "sublevel13_p": "Sub-Level 13",
    "ma_subconscious_p": "Subconscious",
    "ma_subboss_p": "The Cortex",
    "eridian_slaughter_p": "The Holodome",
    "meriff_p": "The Meriff's Office",
    "ma_nexus_p": "The Nexus",
    "dahlfactory_p": "Titan Industrial Facility",
    "dahlfactory_boss": "Titan Robot Production Plant",
    "moon_p": "Triton Flats",
    "access_p": "Tycho's Ribs",
    "innerhull_p": "Veins of Helios",
    "digsite_p": "Vorago Solitude",
}
