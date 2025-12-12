import unrealsdk
import unrealsdk.unreal as unreal
from unrealsdk.hooks import Type, Block
from ui_utils import show_chat_message

import datetime

from mods_base import get_pc, ObjectFlags
from BouncyLootGod.oob import get_loc_in_front_of_player
from BouncyLootGod.archi_defs import gear_kind_to_id

# many things here adapted from RoguelandsGamemode\Looties.py

orange = unrealsdk.make_struct("Color", R=128, G=64, B=0, A=255)

# unused, maybe useful
def pathname(obj):
    return obj.PathName(obj)

def get_or_create_package(package_name="BouncyLootGod"):
    try:
        return unrealsdk.find_object("Package", package_name)
    except ValueError:
        return unrealsdk.construct_object("Package", None, "BouncyLootGod", ObjectFlags.KEEP_ALIVE)

# unused, maybe useful
def call_later(time, call):
    """Call the given callable after the given time has passed."""
    timer = datetime.datetime.now()
    future = timer + datetime.timedelta(seconds=time)

    # Create a wrapper to call the routine that is suitable to be passed to add_hook.
    def tick(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
        # Invoke the routine when enough time has passed and unregister its tick hook.

        if datetime.datetime.now() >= future:
            call()
            unrealsdk.hooks.remove_hook("WillowGame.WillowGameViewportClient:Tick", Type.PRE, "CallLater" + str(call))
        return True

    # Hook the wrapper.
    unrealsdk.hooks.add_hook("WillowGame.WillowGameViewportClient:Tick", Type.PRE, "CallLater" + str(call), tick)

# unused, maybe useful
def temp_set_prop(obj, prop_name, val):
    backup = getattr(obj, prop_name)
    if backup == val:
        print(prop_name + " already set to val")
        return
    setattr(obj, prop_name, val)
    def reset_prop():
        setattr(obj, prop_name, backup)
    call_later(1, reset_prop)

# def set_command(obj, property, value):
#     if isinstance(value, list):
#         command = f"set {pathname(obj)} {property} ({','.join(value)})"
#     else:
#         command = f"set {pathname(obj)} {property} {value}"
#     get_pc().ConsoleCommand(command)


# def temp_set_prop(obj, prop_name, val):
#     backup = getattr(obj, prop_name)
#     if backup == val:
#         print(prop_name + " already set to val")
#         return
#     set_command(obj, prop_name, val)
#     def reset_prop():
#         set_command(obj, prop_name, backup)
#     call_later(1, reset_prop)


# TODO new approach... don't clone balance defs, only loot pools.
# try editing balance defs and switching them back after the spawn is done
# def old_clone_inv_bal_def(
#     inv_bal_def,
#     inv_bal_kind="WeaponBalanceDefinition",
#     package_name="BouncyLootGod",
#     remove_some_min_req=True,
#     relic_rarity="",
#     skip_alien=False,
# ):
#     if type(inv_bal_def) is str:
#         src_inv_bal_def = unrealsdk.find_object(inv_bal_kind, inv_bal_def)
#     else:
#         src_inv_bal_def = inv_bal_def
#         inv_bal_kind = inv_bal_def.Class.Name

#     package = get_or_create_package(package_name)

#     if remove_some_min_req and inv_bal_kind == "WeaponBalanceDefinition":
#         src_rplc = src_inv_bal_def.RuntimePartListCollection
#         if src_rplc:
#             cloned_rplc = unrealsdk.construct_object("WeaponPartListCollectionDefinition", package, src_rplc.Name, 0, src_rplc)
#             if len(cloned_rplc.ElementalPartData.WeightedParts):
#                 for wp in cloned_rplc.ElementalPartData.WeightedParts:
#                     # temp_set_prop(wp, "MinGameStageIndex", 0)
#                     wp.MinGameStageIndex = 0
#                 # temp_set_prop(cloned_rplc, "ElementalPartData", epd)

#             if skip_alien and len(cloned_rplc.BarrelPartData.WeightedParts):
#                 for wp in cloned_rplc.BarrelPartData.WeightedParts:
#                     if "Alien" in wp.Part.Name:
#                         # temp_set_prop(wp, "Part", None)
#                         wp.Part = None
#                 # temp_set_prop(cloned_rplc, "BarrelPartData", bpd)
#                 # for i in reversed(range(len(cloned_rplc.BarrelPartData.WeightedParts))):
#                 #     wp = cloned_rplc.BarrelPartData.WeightedParts[i]
#                 #     if "Alien" in wp.Part.Name:
#                 #         wp.Part = None
#                         # cloned_rplc.BarrelPartData.WeightedParts.pop(i)
#                         # wp.MinGameStageIndex = 255
#                 # src_inv_bal_def.RuntimePartListCollection = cloned_rplc
#             # def reset_rplc():
#             #     show_chat_message("reset_rplc")
#             #     src_inv_bal_def.RuntimePartListCollection = cloned_rplc
#             # call_later(1, reset_rplc)
#             # src_inv_bal_def.RuntimePartListCollection = cloned_rplc
#             temp_set_prop(src_inv_bal_def, "RuntimePartListCollection", cloned_rplc)


#     if remove_some_min_req and inv_bal_kind == "InventoryBalanceDefinition":
#         src_plc = src_inv_bal_def.PartListCollection
#         if src_plc:
#             cloned_plc = unrealsdk.construct_object("ItemPartListCollectionDefinition", package, src_plc.Name, 0, src_plc)
#             # for grenade mod delivery and element
#             for wp in cloned_plc.DeltaPartData.WeightedParts:
#                 # temp_set_prop(wp, "MinGameStageIndex", 0)
#                 wp.MinGameStageIndex = 0
#             for wp in cloned_plc.BetaPartData.WeightedParts:
#                 # temp_set_prop(wp, "MinGameStageIndex", 0)
#                 wp.MinGameStageIndex = 0
            
#             if relic_rarity:
#                 theta_weighted_parts = []
#                 # only include specified relic rarity
#                 # print("\nASDF")
#                 # print(cloned_plc.ThetaPartData == cloned_plc.ThetaPartData)
#                 # print(cloned_plc.ThetaPartData)
#                 # print(cloned_plc.ThetaPartData)
#                 for wp in cloned_plc.ThetaPartData.WeightedParts:
#                     if wp.Part and str(wp.Part.Rarity.BaseValueAttribute.Name).split("_")[-1] == relic_rarity:
#                         theta_weighted_parts.append(wp)
#                 # temp_set_prop(cloned_plc.ThetaPartData, "WeightedParts", theta_weighted_parts)
#                 print("old grade len " + str(len(cloned_plc.ThetaPartData.WeightedParts)))
#                 # print(cloned_plc.ThetaPartData.WeightedParts)
#                 cloned_plc.ThetaPartData.WeightedParts = theta_weighted_parts
#                 # print(cloned_plc.ThetaPartData.WeightedParts)
#                 print("relic grade len " + str(len(theta_weighted_parts)))

#                 # print(len(theta_weighted_parts))
#             # def reset_plc():
#             #     show_chat_message("reset_plc")
#             #     src_inv_bal_def.PartListCollection = cloned_plc
#             # call_later(1, reset_plc)
#             temp_set_prop(src_inv_bal_def, "PartListCollection", cloned_plc)


#         manufacturers = src_inv_bal_def.Manufacturers
#         # allow restricted manufacturers
#         if manufacturers:
#             new_manufacturers = []
#             # cloned_inv_bal_def = unrealsdk.construct_object(inv_bal_kind, package, src_inv_bal_def.Name, 0, src_inv_bal_def)
#             for m in manufacturers:
#                 new_m = unrealsdk.make_struct("InventoryManufacturerBalanceData", Manufacturer=m.Manufacturer, Grades=m.Grades)
#                 new_manufacturers.append(new_m)
#                 for g in new_m.Grades:
#                     g.GameStageRequirement.MinGameStage = 0
#                     # temp_set_prop(g.GameStageRequirement, "MinGameStage", 0)
#             src_inv_bal_def.Manufacturers
#             temp_set_prop(src_inv_bal_def, "Manufacturers", new_manufacturers)
            
#             print("Manufacturers done")

#             # def reset_manufacturers():
#             #     show_chat_message("reset_manufacturers")
#             #     src_inv_bal_def.Manufacturers = cloned_inv_bal_def.Manufacturers
#             # call_later(1, reset_manufacturers)


#     return src_inv_bal_def

# def clone_item_pool(
#     item_pool,
#     package_name="BouncyLootGod",
#     remove_some_min_req=True,
#     relic_rarity="",
#     skip_alien=False
# ):
#     if type(item_pool) is str:
#         src_pool = unrealsdk.find_object("ItemPoolDefinition", item_pool)
#     else:
#         src_pool = item_pool
#     package = get_or_create_package(package_name)
#     cloned_item_pool = unrealsdk.construct_object("ItemPoolDefinition", package, src_pool.Name, 0, src_pool)
#     if remove_some_min_req:
#         cloned_item_pool.MinGameStageRequirement = None
#         for i in range(len(cloned_item_pool.BalancedItems)):
#             if (sub_pool := cloned_item_pool.BalancedItems[i].ItmPoolDefinition):
#                 cloned_sub_pool = clone_item_pool(sub_pool, package_name=package_name, remove_some_min_req=remove_some_min_req, relic_rarity=relic_rarity, skip_alien=skip_alien)
#                 cloned_item_pool.BalancedItems[i].ItmPoolDefinition = cloned_sub_pool
#             elif (inv_bal_def := cloned_item_pool.BalancedItems[i].InvBalanceDefinition):
#                 cloned_inv_bal_def = clone_inv_bal_def(inv_bal_def, package_name=package_name, remove_some_min_req=remove_some_min_req, relic_rarity=relic_rarity, skip_alien=skip_alien)
#                 cloned_item_pool.BalancedItems[i].InvBalanceDefinition = cloned_inv_bal_def

#     return cloned_item_pool


# def construct_item_pool(
#     name,
#     pool_names=[],
#     inv_bal_def_names=[],
#     inv_bal_kind="WeaponBalanceDefinition",
#     package_name="BouncyLootGod",
#     remove_some_min_req=True,
#     src_pool_name=None,
#     relic_rarity="",
#     skip_alien=False
# ):
#     if src_pool_name:
#         item_pool = clone_item_pool(item_pool=src_pool_name, package_name=package_name, remove_some_min_req=remove_some_min_req, relic_rarity=relic_rarity, skip_alien=skip_alien)
#         balanced_items = item_pool.BalancedItems
#     else:
#         package = get_or_create_package(package_name)
#         item_pool = unrealsdk.construct_object("ItemPoolDefinition", package, name)
#         balanced_items = []

#     probability = unrealsdk.make_struct("AttributeInitializationData", BaseValueConstant=1, BaseValueScaleConstant=1)

#     for name in pool_names:
#         pool = clone_item_pool(name, relic_rarity=relic_rarity, skip_alien=skip_alien)
#         balanced_item = unrealsdk.make_struct("BalancedInventoryData", ItmPoolDefinition=pool, Probability=probability, bDropOnDeath=True)
#         balanced_items.append(balanced_item)
    
#     for name in inv_bal_def_names:
#         # clone so we don't mess with regular loot pools
#         cloned_inv_bal_def = clone_inv_bal_def(name, inv_bal_kind=inv_bal_kind, package_name=package_name, remove_some_min_req=remove_some_min_req, relic_rarity=relic_rarity, skip_alien=skip_alien)
#         balanced_item = unrealsdk.make_struct("BalancedInventoryData", InvBalanceDefinition=cloned_inv_bal_def, Probability=probability, bDropOnDeath=True)
#         balanced_items.append(balanced_item)

#     for bi in balanced_items:
#         bi.Probability = probability

#     item_pool.BalancedItems = balanced_items
#     return item_pool

# unused, maybe useful
def override_hook_once(hook, value):
    """override only the next call of the given hook to return the given value."""
    def override_func(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
        unrealsdk.hooks.remove_hook(hook, Type.PRE, "override_hook_once")
        return Block, value
    unrealsdk.hooks.add_hook(hook, Type.PRE, "override_hook_once", override_func)

# new approach... don't clone balance defs, modify and return cleanup functions
def modify_inv_bal_def(
    inv_bal_def,
    relic_rarity="",
    skip_alien=False,
):
    my_cleanup_funcs = []
    m_backup = []
    for m in inv_bal_def.Manufacturers: # restricted manufacturers
        for g in m.Grades:
            m_backup.append(g.GameStageRequirement.MinGameStage)
            g.GameStageRequirement.MinGameStage = 0
    def reset_manufacturers(inv_bal_def, m_backup):
        for m in inv_bal_def.Manufacturers:
            for g in m.Grades:
                g.GameStageRequirement.MinGameStage = m_backup.pop(0)
    r_m_func = lambda inv_bal_def=inv_bal_def, m_backup=m_backup: reset_manufacturers(inv_bal_def, m_backup)
    my_cleanup_funcs.append(r_m_func)

    if (plc := inv_bal_def.PartListCollection):
        bd_backup = []
        for wp in plc.DeltaPartData.WeightedParts: # grenade elements
            bd_backup.append(wp.MinGameStageIndex)
            wp.MinGameStageIndex = 0
        for wp in plc.BetaPartData.WeightedParts: # grenade delivery
            bd_backup.append(wp.MinGameStageIndex)
            wp.MinGameStageIndex = 0
        def reset_bd(inv_bal_def, bd_backup):
            plc = inv_bal_def.PartListCollection
            for wp in plc.DeltaPartData.WeightedParts:
                wp.MinGameStageIndex = bd_backup.pop(0)
            for wp in plc.BetaPartData.WeightedParts:
                wp.MinGameStageIndex = bd_backup.pop(0)
        r_bd_func = lambda inv_bal_def=inv_bal_def, bd_backup=bd_backup: reset_bd(inv_bal_def, bd_backup)
        my_cleanup_funcs.append(r_bd_func)

        if relic_rarity:
            th_backup = []
            for idx in range(len(plc.ThetaPartData.WeightedParts)): # relic grade
                wp = plc.ThetaPartData.WeightedParts[idx]
                th_backup.append(wp.DefaultWeightIndex)
                if wp.Part and not wp.Part.Rarity.BaseValueAttribute.Name.endswith("_" + relic_rarity):
                    wp.DefaultWeightIndex = 7
            def reset_theta(inv_bal_def, th_backup):
                plc = inv_bal_def.PartListCollection
                for wp in plc.ThetaPartData.WeightedParts:
                    wp.DefaultWeightIndex = th_backup.pop(0)
            r_th_func = lambda inv_bal_def=inv_bal_def, th_backup=th_backup: reset_theta(inv_bal_def, th_backup)
            my_cleanup_funcs.append(r_th_func)

    if inv_bal_def.Class.Name == "WeaponBalanceDefinition":
        rplc = inv_bal_def.RuntimePartListCollection
        el_backup = []
        for wp in rplc.ElementalPartData.WeightedParts: # gun elements
            el_backup.append(wp.MinGameStageIndex)
            wp.MinGameStageIndex = 0
        def reset_el(inv_bal_def, el_backup):
            rplc = inv_bal_def.RuntimePartListCollection
            for wp in rplc.ElementalPartData.WeightedParts:
                wp.MinGameStageIndex = el_backup.pop(0)
        r_el_func = lambda inv_bal_def=inv_bal_def, el_backup=el_backup: reset_el(inv_bal_def, el_backup)
        my_cleanup_funcs.append(r_el_func)

        if skip_alien and len(rplc.BarrelPartData.WeightedParts):
            barrel_backup = []
            for wp in rplc.BarrelPartData.WeightedParts: # remove e-tech elements
                if wp.Part is None:
                    barrel_backup.append(wp.Part)
                elif "Alien" in wp.Part.Name:
                    barrel_backup.append(wp.Part)
                    wp.Part = None
            def reset_barrel(inv_bal_def, barrel_backup):
                rplc = inv_bal_def.RuntimePartListCollection
                for wp in rplc.BarrelPartData.WeightedParts:
                    if wp.Part is None:
                        wp.Part = barrel_backup.pop(0)
            r_barrel_func = lambda inv_bal_def=inv_bal_def, barrel_backup=barrel_backup: reset_barrel(inv_bal_def, barrel_backup)
            my_cleanup_funcs.append(r_barrel_func)


    # if (rplc := inv_bal_def.RuntimePartListCollection):
    #     for wp in plc.DeltaPartData.WeightedParts: # grenade elements
    #         bd_backup.append(wp.MinGameStageIndex)
    #         wp.MinGameStageIndex = 0



    return my_cleanup_funcs


def create_modified_item_pool(
    name="itempool",
    base_pool=None,
    pool_names=[],
    inv_bal_def_names=[],
    package_name="BouncyLootGod",
    relic_rarity="",
    skip_alien=False,
    uniform_probability=True,
):
    package = get_or_create_package(package_name)
    if base_pool is None:
        item_pool = unrealsdk.construct_object("ItemPoolDefinition", package, name)
    elif type(base_pool) is str:
        base_pool = unrealsdk.find_object("ItemPoolDefinition", base_pool)
        item_pool = unrealsdk.construct_object("ItemPoolDefinition", package, base_pool.Name, 0, base_pool)
    else:
        item_pool = unrealsdk.construct_object("ItemPoolDefinition", package, base_pool.Name, 0, base_pool)

    item_pool.MinGameStageRequirement = None
    probability = unrealsdk.make_struct("AttributeInitializationData", BaseValueConstant=1, BaseValueScaleConstant=1)
    my_cleanup_funcs = []

    for bi in item_pool.BalancedItems:
        if (sub_pool := bi.ItmPoolDefinition):
            (new_sub_pool, p_cleanup_funcs) = create_modified_item_pool(base_pool=sub_pool, relic_rarity=relic_rarity, skip_alien=skip_alien, package_name=package_name, uniform_probability=uniform_probability)
            bi.ItmPoolDefinition = new_sub_pool
            my_cleanup_funcs.extend(p_cleanup_funcs)
        elif (inv_bal_def := bi.InvBalanceDefinition):
            i_cleanup_funcs = modify_inv_bal_def(inv_bal_def, relic_rarity=relic_rarity, skip_alien=skip_alien)
            my_cleanup_funcs.extend(i_cleanup_funcs)
        if uniform_probability:
            bi.Probability = probability

    # add ibds from params
    for inv_bal_def_name in inv_bal_def_names:
        inv_bal_def = unrealsdk.find_object("InventoryBalanceDefinition", inv_bal_def_name)
        i_cleanup_funcs = modify_inv_bal_def(inv_bal_def, relic_rarity=relic_rarity, skip_alien=skip_alien)
        my_cleanup_funcs.extend(i_cleanup_funcs)
        balanced_item = unrealsdk.make_struct("BalancedInventoryData", InvBalanceDefinition=inv_bal_def, Probability=probability, bDropOnDeath=True)
        item_pool.BalancedItems.append(balanced_item)

    # add pools from params
    for pool_name in pool_names:
        sub_pool = unrealsdk.find_object("ItemPoolDefinition", pool_name)
        (new_sub_pool, p_cleanup_funcs) = create_modified_item_pool(base_pool=sub_pool, relic_rarity=relic_rarity, skip_alien=skip_alien, package_name=package_name, uniform_probability=uniform_probability)
        balanced_item = unrealsdk.make_struct("BalancedInventoryData", ItmPoolDefinition=new_sub_pool, Probability=probability, bDropOnDeath=True)
        item_pool.BalancedItems.append(balanced_item)
        my_cleanup_funcs.extend(p_cleanup_funcs)

    return (item_pool, my_cleanup_funcs)

# obj dump GD_GrenadeMods.A_Item.GM_Singularity

def get_item_pool_from_gear_kind_id(gear_kind_id):
    # (pool, cleanup_funcs) = create_modified_item_pool(base_pool="GD_Itempools.GrenadeModPools.Pool_GrenadeMods_01_Common")
    # return (pool, cleanup_funcs)
    # return unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_01_Common")
    # return gear_kind_to_item_pool.get(gear_kind_id)

    match gear_kind_id:
        # Shield
        case 100:
            return create_modified_item_pool(base_pool="GD_Itempools.ShieldPools.Pool_Shields_All_01_Common")
        case 101:
            return create_modified_item_pool(base_pool="GD_Itempools.ShieldPools.Pool_Shields_All_02_Uncommon")
        case 102:
            return create_modified_item_pool(base_pool="GD_Itempools.ShieldPools.Pool_Shields_All_04_Rare")
        case 103:
            return create_modified_item_pool(base_pool="GD_Itempools.ShieldPools.Pool_Shields_All_05_VeryRare")
            # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_CrackedSash",

        case 105:
            return create_modified_item_pool("BLGLegendaryShields", inv_bal_def_names=[
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Singularity",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryShock",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryNormal",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_ThresherRaid",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Phoenix",
            ])
        case 106:
            return create_modified_item_pool("BLGSeraphShields",
                inv_bal_def_names=[
                    "GD_Aster_ItemGrades.Shields.Aster_Seraph_Blockade_Shield_Balance",
                    "GD_Aster_ItemGrades.Shields.Aster_Seraph_Antagonist_Shield_Balance",
                    "GD_Iris_SeraphItems.BigBoomBlaster.Iris_Seraph_Shield_Booster_Balance",
                    "GD_Iris_SeraphItems.Hoplite.Iris_Seraph_Shield_Juggernaut_Balance",
                    "GD_Iris_SeraphItems.Pun-chee.Iris_Seraph_Shield_Pun-chee_Balance",
                    "GD_Iris_SeraphItems.Sponge.Iris_Seraph_Shield_Sponge_Balance",
                    "GD_Orchid_RaidWeapons.Shield.Anshin.Orchid_Seraph_Anshin_Shield_Balance",
                ]
            )
        case 107:
            return create_modified_item_pool("BLGRainbowShields",
                inv_bal_def_names=[
                    "GD_Anemone_ItemPools.Shields.ItemGrade_Gear_Shield_Nova_Singularity_Peak", # has high spawn modifier
                    # "GD_Anemone_Balance_Treasure.Shields.ItemGrade_Gear_Shield_Worming",
                ],
                pool_names=[
                    "GD_Anemone_ItemPools.ShieldPools.Pool_Shields_Standard_06_Legendary",
                ]
            )
        case 109:
            return create_modified_item_pool("BLGUniqueShields",
                inv_bal_def_names=[
                    "GD_Orchid_Shields.A_Item_Custom.S_BladeShield",
                    "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_1340",
                    "GD_Sage_Shields.A_Item_Custom.S_BucklerShield",
                    "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_PotOGold",
                    "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_Order",
                    "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_Equitas",
                    "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_DeadlyBloom",
                    "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_04_LoveThumper",
                ]
            )

        # GrenadeMod
        case 110:
            return create_modified_item_pool(base_pool="GD_Itempools.GrenadeModPools.Pool_GrenadeMods_01_Common")
        case 111:
            return create_modified_item_pool(base_pool="GD_Itempools.GrenadeModPools.Pool_GrenadeMods_02_Uncommon")
        case 112:
            return create_modified_item_pool(base_pool="GD_Itempools.GrenadeModPools.Pool_GrenadeMods_04_Rare")
        case 113:
            return create_modified_item_pool(base_pool="GD_Itempools.GrenadeModPools.Pool_GrenadeMods_05_VeryRare")
        case 115:
            return create_modified_item_pool("BLGLegendaryGrenadeMods", 
                base_pool="GD_Itempools.GrenadeModPools.Pool_GrenadeMods_06_Legendary",
                inv_bal_def_names=[
                    "GD_Aster_GrenadeMods.A_Item.GM_FireStorm",
                    "GD_Aster_GrenadeMods.A_Item.GM_ChainLightning",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_BonusPackage",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_BouncingBonny",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_Fastball",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_FireBee",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_Leech",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_Pandemic",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_Quasar",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_RollingThunder",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_StormFront",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_NastySurprise",
                ]
            )
        case 119:
            return create_modified_item_pool(base_pool="BLGUniqueGrenadeMods",
                inv_bal_def_names=[
                    "GD_Aster_GrenadeMods.A_Item.GM_Fireball",
                    "GD_Aster_GrenadeMods.A_Item.GM_LightningBolt",
                    "GD_Aster_GrenadeMods.A_Item.GM_MagicMissileRare",
                    "GD_Orchid_GrenadeMods.A_Item_Custom.GM_Blade",
                    "GD_GrenadeMods.A_Item_Custom.GM_FusterCluck",
                    "GD_GrenadeMods.A_Item_Custom.GM_KissOfDeath",
                    "GD_GrenadeMods.A_Item_Custom.GM_SkyRocket",
                ]
            )

        # ClassMod
        case 120:
            # return (unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.ClassModPools.Pool_ClassMod_01_Common"), [])
            return create_modified_item_pool(base_pool="GD_Itempools.ClassModPools.Pool_ClassMod_01_Common", uniform_probability=False)
        case 121:
            return create_modified_item_pool(base_pool="GD_Itempools.ClassModPools.Pool_ClassMod_02_Uncommon", uniform_probability=False)
        case 122:
            return create_modified_item_pool(base_pool="GD_Itempools.ClassModPools.Pool_ClassMod_04_Rare", uniform_probability=False)
        case 123:
            return create_modified_item_pool(base_pool="GD_Itempools.ClassModPools.Pool_ClassMod_05_VeryRare", uniform_probability=False)
        case 125:
            return create_modified_item_pool("BLGLegendaryClassMods",
                inv_bal_def_names=[
                    # "GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Soldier_05_Legendary",
                ],
                pool_names=[
                    "GD_Itempools.ClassModPools.Pool_ClassMod_06_Legendary",
                    "GD_Itempools.ClassModPools.Pool_ClassMod_06_SlayerOfTerramorphous",
                    # lobelia has 3 elements per character, so add it 3 times to balance
                    "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All", 
                    "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All",
                    "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All",
                ],
                uniform_probability=False,
            )

        # Relic
        case 130:
            return create_modified_item_pool("BLGCommonRelic",
                base_pool="GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
                relic_rarity="Common",
            )
        case 131:
            return create_modified_item_pool("BLGUncommonRelic",
                base_pool="GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
                relic_rarity="Uncommon",
            )
        case 132:
            return create_modified_item_pool("BLGRareRelic",
                # base_pool="GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
                base_pool="GD_Itempools.ArtifactPools.Pool_Artifacts_03_Rare", # this should work but produces white relics. no clue.
                relic_rarity="Rare",
            )
        case 133:
            return create_modified_item_pool("BLGVeryRareRelic",
                base_pool="GD_Itempools.ArtifactPools.Pool_Artifacts_03_Rare",
                relic_rarity="VeryRare",
            )
        case 134:
            return create_modified_item_pool("BLGETechRelic",
                pool_names=[
                    "GD_Gladiolus_Itempools.ArtifactPools.Pool_Artifacts_Ancient_AggressionTenacity"
                ],
                inv_bal_def_names=[
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityAssault_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityLauncher_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityPistol_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityShotgun_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacitySMG_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacitySniper_VeryRare",
                    "GD_Gladiolus_Artifacts.A_Item.A_ElementalProficiency_VeryRare",
                    "GD_Gladiolus_Artifacts.A_Item.A_ResistanceProtection_VeryRare",
                    "GD_Gladiolus_Artifacts.A_Item.A_VitalityStockpile_VeryRare",
                ],
            )
        # case 135:
            # "GD_Artifacts.A_Item_Unique.A_Terramorphous",
        # case 136:
            # blood
            # breath
            # might
            # shadow
        # case 137:
            # hard carry
            # mouthwash
        # case 138:
        case 139:
            return create_modified_item_pool("BLGUniqueRelic",
                inv_bal_def_names=[
                    "GD_Artifacts.A_Item_Unique.A_Afterburner",
                    "GD_Artifacts.A_Item_Unique.A_Deputy",
                    "GD_Artifacts.A_Item_Unique.A_Endowment",
                    "GD_Artifacts.A_Item_Unique.A_Opportunity",
                    "GD_Artifacts.A_Item_Unique.A_Sheriff",
                    "GD_Artifacts.A_Item_Unique.A_VaultHunter",
                    "GD_Aster_Artifacts.A_Item_Unique.A_MysteryAmulet",
                ],
            )

        # Pistol
        case 140:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_01_Common") # Maliwan breaks for this
            # return create_modified_item_pool("BLGWhitePistols",
            #     inv_bal_def_names=[
            #         "GD_Weap_Pistol.A_Weapons.Pistol_Bandit",
            #         "GD_Weap_Pistol.A_Weapons.Pistol_Tediore",
            #         "GD_Weap_Pistol.A_Weapons.Pistol_Dahl",
            #         "GD_Weap_Pistol.A_Weapons.Pistol_Vladof",
            #         "GD_Weap_Pistol.A_Weapons.Pistol_Torgue",
            #         "GD_Weap_Pistol.A_Weapons.Pistol_Jakobs",
            #         "GD_Weap_Pistol.A_Weapons.Pistol_Hyperion",
            #         "GD_Weap_Pistol.A_Weapons.Pistol_Maliwan", # Maliwan has to be at the end? no idea what's going on
            #     ]
            # )
        case 141:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_02_Uncommon")
        case 142:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_04_Rare")
        case 143:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare", skip_alien=True)
        case 144:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare_Alien")
        case 145:
            return create_modified_item_pool("BLGLegendaryPistols",
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_06_Legendary",
                pool_names=[
                    "GD_Anemone_ItemPools.WeaponPools.Pool_Pistol_Hector_Paradise",
                ]
            )
        # case 146:
            # stinger
            # infection
            # devastator
            # GD_Orchid_RaidWeapons.Pistol.Devastator.Orchid_Seraph_Devastator_Balance

        # case 147:
            # n/a
        # case 148:
            # "GD_Lobelia_Weapons.Pistol.Pistol_Maliwan_6_Wanderlust",
            # "GD_Gladiolus_Weapons.Pistol.Pistol_Jakobs_6_Unforgiven",
            # "GD_Gladiolus_Weapons.Pistol.Pistol_Vladof_6_Stalker",
        case 149:
            return create_modified_item_pool("BLGUniquePistols",
                inv_bal_def_names=[
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Fibber",
                    "GD_Orchid_BossWeapons.Pistol.Pistol_Jakobs_ScarletsGreed",
                    "GD_Aster_Weapons.Pistols.Pistol_Maliwan_3_GrogNozzle",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_GwensHead",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Judge",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_LadyFist",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Law",
                    "GD_Orchid_BossWeapons.Pistol.Pistol_Maliwan_3_LittleEvie",
                    "GD_Iris_Weapons.Pistols.Pistol_Torgue_3_PocketRocket",
                    "GD_Sage_Weapons.Pistols.Pistol_Jakobs_3_Rex",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Maliwan_3_Rubi",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Teapot",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Bandit_3_Tenderbox",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Vladof_3_Veritas",
                    # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_Starter",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Dahlminator",
                ],
                pool_names=[]
            )

        # Shotgun
        case 150:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_01_Common")
        case 151:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_02_Uncommon")
        case 152:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_04_Rare")
        case 153:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare")
        case 154:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare_Alien")
        case 155:
            return create_modified_item_pool("BLGLegendaryShotguns", 
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_06_Legendary",
                inv_bal_def_names=[
                    "GD_Anemone_Weapons.Shotgun.Overcompensator.SG_Hyperion_6_Overcompensator"
                ]
            )

        # case   156:
            # retcher
            #GD_Orchid_RaidWeapons.Shotgun.Spitter.Orchid_Seraph_Spitter_Balance

            # omen
            # interfacer
        # case   157:
            # GD_Anemone_Weapons.Shotguns.SG_Torgue_3_SwordSplosion_Unico
        # case   158:
            # "GD_Gladiolus_Weapons.Shotgun.SG_Hyperion_6_Butcher",
            # "GD_Lobelia_Weapons.Shotguns.SG_Torgue_6_Carnage",
        case 159:
            return create_modified_item_pool("BLGUniqueShotguns",
                inv_bal_def_names=[
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Blockhead",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Dog",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_HeartBreaker",
                    "GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Hydra",
                    "GD_Orchid_BossWeapons.Shotgun.SG_Bandit_3_JollyRoger",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_Landscaper",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Octo",
                    "GD_Orchid_BossWeapons.Shotgun.SG_Jakobs_3_OrphanMaker",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_RokSalt",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_Shotgun1340",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Teeth",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_TidalWave",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_Triquetra",
                    "GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Twister",
                    "GD_Aster_Weapons.Shotguns.SG_Torgue_3_SwordSplosion",
                    "GD_Iris_Weapons.Shotguns.SG_Hyperion_3_SlowHand",
                ],
                pool_names=[]
            )

        # SMG
        case 160:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SMG_01_Common")  # has Maliwan issue.
            # return construct_item_pool("BLGWhiteSMGs",
            #     inv_bal_def_names=[
            #         "GD_Weap_SMG.A_Weapons.SMG_Bandit",
            #         "GD_Weap_SMG.A_Weapons.SMG_Tediore",
            #         "GD_Weap_SMG.A_Weapons.SMG_Dahl",
            #         "GD_Weap_SMG.A_Weapons.SMG_Hyperion",
            #         "GD_Weap_SMG.A_Weapons.SMG_Maliwan", # Maliwan has to be at the end?
            #     ]
            # )

        case 161:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SMG_02_Uncommon")
        case 162:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SMG_04_Rare")
        case 163:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SMG_05_VeryRare")
        case 164:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SMG_05_VeryRare_Alien")
        case 165:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SMG_06_Legendary")
        # case   166:
            # Tattler
            # GD_Orchid_RaidWeapons.SMG.Tattler.Orchid_Seraph_Tattler_Balance
            # Florentine
            # 'GD_Aster_RaidWeapons.SMGs.Aster_Seraph_Florentine_Balance',
            # Actualizer
            # GD_Orchid_RaidWeapons.SMG.Actualizer.Orchid_Seraph_Actualizer_Balance

        # case   167:
            # Nirvana
            # Infection Cleaner
        # case   168:
            # "GD_Gladiolus_Weapons.SMG.SMG_Tediore_6_Avenger",
        case 169:
            return create_modified_item_pool("BLGUniqueSMGs",
                inv_bal_def_names=[
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Bandit_3_BoneShredder",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Dahl_3_Lascaux",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Gearbox_1",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Bane",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Commerce",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_Chulainn",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_GoodTouch",
                    "GD_Sage_Weapons.SMG.SMG_Hyperion_3_YellowJacket",
                    "GD_Orchid_BossWeapons.SMG.SMG_Dahl_3_SandHawk",
                    "GD_Aster_Weapons.SMGs.SMG_Bandit_3_Orc",
                    "GD_Aster_Weapons.SMGs.SMG_Maliwan_3_Crit",
                ],
                pool_names=[]
            )

        # SniperRifle
        case 170:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_01_Common") # has Maliwan issue.
            # return construct_item_pool("BLGWhiteSniperRifles",
            #     inv_bal_def_names=[
            #         "GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl",
            #         "GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof",
            #         "GD_Weap_SniperRifles.A_Weapons.Sniper_Jakobs",
            #         "GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion",
            #         "GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan", # Maliwan has to be at the end?
            #     ]
            # )

        case 171:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_02_Uncommon")
        case 172:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_04_Rare")
        case 173:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_05_VeryRare", skip_alien=True)
        case 174:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_05_VeryRare_Alien")
        case 175:
            return create_modified_item_pool(
                "BLGLegendarySnipers", 
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_06_Legendary",
                inv_bal_def_names=[
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Dahl_5_Pitchfork",
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Vladof_5_Lyudmila",
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Maliwan_5_Volcano",
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Jakobs_5_Skullmasher",
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Hyperion_5_Invader",
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Longbow",
                    "GD_Anemone_Weapons.A_Weapons_Unique.Sniper_Jakobs_3_Morde_Lt",
                ]
            )
        # case   176:
            # Patriot
            # GD_Orchid_RaidWeapons.sniper.Patriot.Orchid_Seraph_Patriot_Balance
            # Hawk Eye
        # case   177:
            # Hot Mama
        # case   178:
            # Storm
            # "GD_Gladiolus_Weapons.sniper.Sniper_Maliwan_6_Storm",

            # Godfinger
            # GD_Lobelia_Weapons.sniper.SR_Body_Jakobs_6_GodFinger
        case 179:
            return create_modified_item_pool("BLGUniqueSnipers",
                inv_bal_def_names=[
                    "GD_Sage_Weapons.SniperRifles.Sniper_Jakobs_3_ElephantGun",
                    "GD_Orchid_BossWeapons.SniperRifles.Sniper_Maliwan_3_Pimpernel",
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Buffalo",
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Maliwan_3_ChereAmie",
                    "GD_Iris_Weapons.SniperRifles.Sniper_Jakobs_3_Cobra",
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_FremingtonsEdge",
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Morningstar",
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Dahl_3_Sloth",
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Tresspasser",
                    # "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Gearbox_1",

                    # GD_Aster_Weapons.Snipers.SR_Dahl_4_Emerald
                    # GD_Aster_Weapons.Snipers.SR_Hyperion_4_Diamond
                    # GD_Aster_Weapons.Snipers.SR_Jakobs_4_Citrine
                    # GD_Aster_Weapons.Snipers.SR_Maliwan_4_Aquamarine
                    # GD_Aster_Weapons.Snipers.SR_Vladof_4_Garnet
                ],
                pool_names=[]
            )

        # AssaultRifle
        case 180:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_01_Common")
        case 181:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_02_Uncommon")
        case 182:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_04_Rare")
        case 183:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare")
        case 184:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare_Alien")
        case 185:
            return create_modified_item_pool(
                "BLGLegendaryARs",
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_06_Legendary",
                inv_bal_def_names=[
                    "GD_Aster_Weapons.AssaultRifles.AR_Bandit_3_Ogre"
                ]
            )
        # case   186:
            # seraphim
            # GD_Orchid_RaidWeapons.AssaultRifle.Seraphim.Orchid_Seraph_Seraphim_Balance

            # seeker
            # 'GD_Aster_RaidWeapons.AssaultRifles.Aster_Seraph_Seeker_Balance',

            # leadstorm
        # case   187:
            # toothpick
            # peak opener
        # case   188:
            # sawbar
            # "GD_Gladiolus_Weapons.AssaultRifle.AR_Bandit_6_Sawbar",
            # bekah
            # GD_Lobelia_Weapons.AssaultRifles.AR_Jakobs_6_Bekah
            # bearcat
            # "GD_Gladiolus_Weapons.AssaultRifle.AR_Dahl_6_Bearcat",

        case 189:
            return create_modified_item_pool("BLGUniqueARs",
                inv_bal_def_names=[
                    "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_3_Scorpio",
                    "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Jakobs_3_Stomper",
                    "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Torgue_3_EvilSmasher",
                    "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Vladof_3_Hail",
                    "GD_Sage_Weapons.AssaultRifle.AR_Jakobs_3_DamnedCowboy",
                    "GD_Sage_Weapons.AssaultRifle.AR_Bandit_3_Chopper",
                    "GD_Iris_Weapons.AssaultRifles.AR_Torgue_3_BoomPuppy",
                    "GD_Iris_Weapons.AssaultRifles.AR_Vladof_3_Kitten",
                    "GD_Orchid_BossWeapons.AssaultRifle.AR_Jakobs_3_Stinkpot",
                    "GD_Orchid_BossWeapons.AssaultRifle.AR_Vladof_3_Rapier",
                    # GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_1_GBX
                ],
                pool_names=[]
            )

        # RocketLauncher
        case 190:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_01_Common") # has Maliwan issue.
            # return construct_item_pool("BLGWhiteRPGs",
            #     inv_bal_def_names=[
            #         "GD_Weap_Launchers.A_Weapons.RL_Bandit",
            #         "GD_Weap_Launchers.A_Weapons.RL_Tediore",
            #         "GD_Weap_Launchers.A_Weapons.RL_Vladof",
            #         "GD_Weap_Launchers.A_Weapons.RL_Torgue",
            #         "GD_Weap_Launchers.A_Weapons.RL_Bandit",
            #         "GD_Weap_Launchers.A_Weapons.RL_Maliwan", # Maliwan has to be at the end?
            #     ]
            # )

        case 191:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_02_Uncommon")
        case 192:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_04_Rare")
        case 193:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_05_VeryRare")
        case 194:
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_05_VeryRare_Alien")
        case 195:
            # issue with this one? Refusing to set array property to itself
            return create_modified_item_pool("BLGLegendaryRPGs",
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_06_Legendary",
                inv_bal_def_names=[
                    "GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_Alien_Norfleet"
                ]
            )

        # case   196:
            # GD_Orchid_RaidWeapons.RPG.Ahab.Orchid_Seraph_Ahab_Balance

        # case   197:
            # WorldBurn
        # case   198:
            # Tunguska 
            # "GD_Gladiolus_Weapons.Launchers.RL_Torgue_6_Tunguska",
        case 199:
            return create_modified_item_pool("BLGUniqueRPGs",
                inv_bal_def_names=[
                    "GD_Weap_Launchers.A_Weapons_Unique.RL_Bandit_3_Roaster",
                    "GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_3_TheHive",
                    "GD_Weap_Launchers.A_Weapons_Unique.RL_Torgue_3_Creamer",
                    "GD_Orchid_BossWeapons.Launcher.RL_Torgue_3_12Pounder",
                ],
                pool_names=[]
            )

        case 2000:
            return (unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_YellowCandy"), [])
        case 2001:
            return (unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_RedCandy"), [])
        case 2002:
            return (unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_GreenCandy"), [])
        case 2003:
            return (unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_BlueCandy"), [])
        case 2004:
            return (unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_Candy"), [])
        case 2005:
            return create_modified_item_pool("BLGMoxxiGuns",
                inv_bal_def_names=[
                    "GD_Weap_Launchers.A_Weapons_Unique.RL_Torgue_3_Creamer",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_GoodTouch",
                    "GD_Aster_Weapons.SMGs.SMG_Maliwan_3_Crit",
                    "GD_Aster_Weapons.Pistols.Pistol_Maliwan_3_GrogNozzle",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Maliwan_3_Rubi",
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Maliwan_3_ChereAmie",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_HeartBreaker",
                    "GD_Iris_Weapons.Shotguns.SG_Hyperion_3_SlowHand",
                    "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Vladof_3_Hail",
                    "GD_Iris_Weapons.AssaultRifles.AR_Vladof_3_Kitten",
                ],
                pool_names=[]
            )
        case 2006:
            return create_modified_item_pool("BLGGemstoneAll",
                inv_bal_def_names=[
                    "GD_Aster_Weapons.AssaultRifles.AR_Bandit_4_Quartz",
                    "GD_Aster_Weapons.AssaultRifles.AR_Dahl_4_Emerald",
                    "GD_Aster_Weapons.AssaultRifles.AR_Jakobs_4_Citrine",
                    "GD_Aster_Weapons.AssaultRifles.AR_Torgue_4_Rock",
                    "GD_Aster_Weapons.AssaultRifles.AR_Vladof_4_Garnet",

                    "GD_Aster_Weapons.Snipers.SR_Dahl_4_Emerald",
                    "GD_Aster_Weapons.Snipers.SR_Hyperion_4_Diamond",
                    "GD_Aster_Weapons.Snipers.SR_Jakobs_4_Citrine",
                    "GD_Aster_Weapons.Snipers.SR_Maliwan_4_Aquamarine",
                    "GD_Aster_Weapons.Snipers.SR_Vladof_4_Garnet",

                    "GD_Aster_Weapons.SMGs.SMG_Bandit_4_Quartz",
                    "GD_Aster_Weapons.SMGs.SMG_Dahl_4_Emerald",
                    "GD_Aster_Weapons.SMGs.SMG_Hyperion_4_Diamond",
                    "GD_Aster_Weapons.SMGs.SMG_Maliwan_4_Aquamarine",
                    "GD_Aster_Weapons.SMGs.SMG_Tediore_4_CubicZerconia",

                    "GD_Aster_Weapons.Shotguns.SG_Bandit_4_Quartz",
                    "GD_Aster_Weapons.Shotguns.SG_Hyperion_4_Diamond",
                    "GD_Aster_Weapons.Shotguns.SG_Jakobs_4_Citrine",
                    "GD_Aster_Weapons.Shotguns.SG_Tediore_4_CubicZerconia",
                    "GD_Aster_Weapons.Shotguns.SG_Torgue_4_Rock",

                    "GD_Aster_Weapons.Pistols.Pistol_Bandit_4_Quartz",
                    "GD_Aster_Weapons.Pistols.Pistol_Dahl_4_Emerald",
                    "GD_Aster_Weapons.Pistols.Pistol_Hyperion_4_Diamond",
                    "GD_Aster_Weapons.Pistols.Pistol_Jakobs_4_Citrine",
                    "GD_Aster_Weapons.Pistols.Pistol_Maliwan_4_Aquamarine",
                    "GD_Aster_Weapons.Pistols.Pistol_Tediore_4_CubicZerconia",
                    "GD_Aster_Weapons.Pistols.Pistol_Torgue_4_Rock",
                    "GD_Aster_Weapons.Pistols.Pistol_Vladof_4_Garnet",
                ],

                pool_names=[]
            )
        case 2007:
            return create_modified_item_pool(base_pool="GD_Aster_ItemPools.WeaponPools.Pool_Weapons_Pistols_04_Gemstone")
            # return create_modified_item_pool("BLGGemstonePistol",
            #     inv_bal_def_names=[
            #         "GD_Aster_Weapons.Pistols.Pistol_Bandit_4_Quartz",
            #         "GD_Aster_Weapons.Pistols.Pistol_Dahl_4_Emerald",
            #         "GD_Aster_Weapons.Pistols.Pistol_Hyperion_4_Diamond",
            #         "GD_Aster_Weapons.Pistols.Pistol_Jakobs_4_Citrine",
            #         "GD_Aster_Weapons.Pistols.Pistol_Maliwan_4_Aquamarine",
            #         "GD_Aster_Weapons.Pistols.Pistol_Tediore_4_CubicZerconia",
            #         "GD_Aster_Weapons.Pistols.Pistol_Torgue_4_Rock",
            #         "GD_Aster_Weapons.Pistols.Pistol_Vladof_4_Garnet",
            #     ],

            #     pool_names=[]
            # )

        case 2008:
            return create_modified_item_pool(base_pool="GD_Aster_ItemPools.WeaponPools.Pool_Weapons_Shotguns_04_Gemstone")

            # return create_modified_item_pool("BLGGemstoneShotgun",
            #     inv_bal_def_names=[
            #         "GD_Aster_Weapons.Shotguns.SG_Bandit_4_Quartz",
            #         "GD_Aster_Weapons.Shotguns.SG_Hyperion_4_Diamond",
            #         "GD_Aster_Weapons.Shotguns.SG_Jakobs_4_Citrine",
            #         "GD_Aster_Weapons.Shotguns.SG_Tediore_4_CubicZerconia",
            #         "GD_Aster_Weapons.Shotguns.SG_Torgue_4_Rock",
            #     ],

            #     pool_names=[]
            # )

        case 2009:
            return create_modified_item_pool(base_pool="GD_Aster_ItemPools.WeaponPools.Pool_Weapons_SMGs_04_Gemstone")

            # return create_modified_item_pool("BLGGemstoneSMG",
            #     inv_bal_def_names=[
            #         "GD_Aster_Weapons.SMGs.SMG_Bandit_4_Quartz",
            #         "GD_Aster_Weapons.SMGs.SMG_Dahl_4_Emerald",
            #         "GD_Aster_Weapons.SMGs.SMG_Hyperion_4_Diamond",
            #         "GD_Aster_Weapons.SMGs.SMG_Maliwan_4_Aquamarine",
            #         "GD_Aster_Weapons.SMGs.SMG_Tediore_4_CubicZerconia",
            #     ],
            #     pool_names=[]
            # )
        case 2010:
            return create_modified_item_pool(base_pool="GD_Aster_ItemPools.WeaponPools.Pool_Weapons_Snipers_04_Gemstone")
            # return create_modified_item_pool("BLGGemstoneSniper",
            #     inv_bal_def_names=[
            #         "GD_Aster_Weapons.Snipers.SR_Dahl_4_Emerald",
            #         "GD_Aster_Weapons.Snipers.SR_Hyperion_4_Diamond",
            #         "GD_Aster_Weapons.Snipers.SR_Jakobs_4_Citrine",
            #         "GD_Aster_Weapons.Snipers.SR_Maliwan_4_Aquamarine",
            #         "GD_Aster_Weapons.Snipers.SR_Vladof_4_Garnet",
            #     ],
            #     pool_names=[]
            # )
        case 2011:
            return create_modified_item_pool(base_pool="GD_Aster_ItemPools.WeaponPools.Pool_Weapons_ARs_04_Gemstone")
            # return create_modified_item_pool("BLGGemstoneAssaultRifle",
            #     inv_bal_def_names=[
            #         "GD_Aster_Weapons.AssaultRifles.AR_Bandit_4_Quartz",
            #         "GD_Aster_Weapons.AssaultRifles.AR_Dahl_4_Emerald",
            #         "GD_Aster_Weapons.AssaultRifles.AR_Jakobs_4_Citrine",
            #         "GD_Aster_Weapons.AssaultRifles.AR_Torgue_4_Rock",
            #         "GD_Aster_Weapons.AssaultRifles.AR_Vladof_4_Garnet",
            #     ],
            #     pool_names=[]
            # )
    return (None, [])

def spawn_gear(gear_kind, dist=150, height=0):
    if type(gear_kind) is int:
        gear_kind_id = gear_kind
    else:
        gear_kind_id = gear_kind_to_id.get(gear_kind, -1)

    (item_pool, cleanup_funcs) = get_item_pool_from_gear_kind_id(gear_kind_id)
    # if not item_pool or item_pool is None:
    #     print("can't find item pool: " + item_pool_name)
    #     return
    spawn_gear_from_pool(item_pool, dist, height, cleanup_funcs=cleanup_funcs)

def spawn_gear_from_pool_name(item_pool_name, dist=150, height=0):
    item_pool = unrealsdk.find_object("ItemPoolDefinition", item_pool_name)
    if not item_pool or item_pool is None:
        print("can't find item pool: " + item_pool_name)
        return
    spawn_gear_from_pool(item_pool, dist, height)


def spawn_gear_from_pool(item_pool, dist=150, height=0, package_name="BouncyLootGod", cleanup_funcs=[]):
    if not item_pool:
        return

    # spawns item at player
    pc = get_pc()
    if not pc or not pc.Pawn:
        print("skipped spawn")
        return
    package = get_or_create_package(package_name)

    sbsl_obj = unrealsdk.construct_object("Behavior_SpawnLootAroundPoint", package, "blg_spawn")
    # sbsl_obj.ItemPools = [unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.WeaponPools.Pool_Weapons_Pistols_02_Uncommon")]
    sbsl_obj.SpawnVelocityRelativeTo = 0
    sbsl_obj.bTorque = False
    sbsl_obj.CircularScatterRadius = 0
    # loc = pc.LastKnownLocation
    loc = get_loc_in_front_of_player(dist, height, pc)
    sbsl_obj.CustomLocation = unrealsdk.make_struct("AttachmentLocationData", 
        Location=loc, #unrealsdk.make_struct("Vector", X=loc.X, Y=loc.Y, Z=loc.Z),
        AttachmentBase=None, AttachmentName=""
    )

    # item_pool.MinGameStageRequirement = None
    sbsl_obj.ItemPools = [item_pool]

    sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=0.000000, Y=0.000000, Z=200.000000)
    sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))

    for func in cleanup_funcs:
        func()
    # 4 direction spawn
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=100.000000, Y=0.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=-100.000000, Y=0.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=0.000000, Y=100.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=0.000000, Y=-100.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))


'''
# attempted dictionary to preload, can't load some things that early, ex. blockade
gear_kind_to_item_pool = {
    100: clone_item_pool("GD_Itempools.ShieldPools.Pool_Shields_All_01_Common"),
    101: clone_item_pool("GD_Itempools.ShieldPools.Pool_Shields_All_02_Uncommon"),
    102: clone_item_pool("GD_Itempools.ShieldPools.Pool_Shields_All_04_Rare"),
    103: clone_item_pool("GD_Itempools.ShieldPools.Pool_Shields_All_05_VeryRare"),
    105: construct_item_pool("BLGLegendaryShields", inv_bal_kind="InventoryBalanceDefinition", inv_bal_def_names=[
        "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_05_Legendary",
        "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Singularity",
        "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_05_Legendary",
        "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_05_Legendary",
        "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_05_Legendary",
        "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryShock",
        "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryNormal",
        "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_05_Legendary",
        "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_05_Legendary",
        "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_ThresherRaid",
        "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Phoenix",
    ]),
    106: construct_item_pool("BLGSeraphShields", inv_bal_kind="InventoryBalanceDefinition",
        inv_bal_def_names=[
            "GD_Aster_ItemGrades.Shields.Aster_Seraph_Blockade_Shield_Balance",
            "GD_Aster_ItemGrades.Shields.Aster_Seraph_Antagonist_Shield_Balance",
            "GD_Iris_SeraphItems.BigBoomBlaster.Iris_Seraph_Shield_Booster_Balance",
            "GD_Iris_SeraphItems.Hoplite.Iris_Seraph_Shield_Juggernaut_Balance",
            "GD_Iris_SeraphItems.Pun-chee.Iris_Seraph_Shield_Pun-chee_Balance",
            "GD_Iris_SeraphItems.Sponge.Iris_Seraph_Shield_Sponge_Balance",
            "GD_Orchid_RaidWeapons.Shield.Anshin.Orchid_Seraph_Anshin_Shield_Balance",
        ]
    ),
    107: construct_item_pool("BLGRainbowShields", inv_bal_kind="InventoryBalanceDefinition",
        inv_bal_def_names=[
            "GD_Anemone_ItemPools.Shields.ItemGrade_Gear_Shield_Nova_Singularity_Peak", # has high spawn modifier
            # "GD_Anemone_Balance_Treasure.Shields.ItemGrade_Gear_Shield_Worming",
        ],
        pool_names=[
            "GD_Anemone_ItemPools.ShieldPools.Pool_Shields_Standard_06_Legendary",
        ]
    ),
    109: construct_item_pool("BLGUniqueShields", inv_bal_kind="InventoryBalanceDefinition",
        inv_bal_def_names=[
            "GD_Orchid_Shields.A_Item_Custom.S_BladeShield",
            "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_1340",
            "GD_Sage_Shields.A_Item_Custom.S_BucklerShield",
            "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_PotOGold",
            "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_Order",
            "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_Equitas",
            "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_DeadlyBloom",
            "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_04_LoveThumper",
        ]
    ),
    110: clone_item_pool("GD_Itempools.GrenadeModPools.Pool_GrenadeMods_01_Common"),
    111: clone_item_pool("GD_Itempools.GrenadeModPools.Pool_GrenadeMods_02_Uncommon"),
    112: clone_item_pool("GD_Itempools.GrenadeModPools.Pool_GrenadeMods_04_Rare"),
    113: clone_item_pool("GD_Itempools.GrenadeModPools.Pool_GrenadeMods_05_VeryRare"),
    115: construct_item_pool("BLGLegendaryGrenadeMods", 
        src_pool_name="GD_Itempools.GrenadeModPools.Pool_GrenadeMods_06_Legendary",
        inv_bal_kind="InventoryBalanceDefinition",
        inv_bal_def_names=[
            "GD_Aster_GrenadeMods.A_Item.GM_FireStorm",
            "GD_Aster_GrenadeMods.A_Item.GM_ChainLightning",
            # "GD_GrenadeMods.A_Item_Legendary.GM_BonusPackage",
            # "GD_GrenadeMods.A_Item_Legendary.GM_BouncingBonny",
            # "GD_GrenadeMods.A_Item_Legendary.GM_Fastball",
            # "GD_GrenadeMods.A_Item_Legendary.GM_FireBee",
            # "GD_GrenadeMods.A_Item_Legendary.GM_Leech",
            # "GD_GrenadeMods.A_Item_Legendary.GM_Pandemic",
            # "GD_GrenadeMods.A_Item_Legendary.GM_Quasar",
            # "GD_GrenadeMods.A_Item_Legendary.GM_RollingThunder",
            # "GD_GrenadeMods.A_Item_Legendary.GM_StormFront",
            # "GD_GrenadeMods.A_Item_Legendary.GM_NastySurprise",
        ]
    ),
    119: construct_item_pool("BLGUniqueGrenadeMods",
        inv_bal_kind="InventoryBalanceDefinition",
        inv_bal_def_names=[
            "GD_Aster_GrenadeMods.A_Item.GM_Fireball",
            "GD_Aster_GrenadeMods.A_Item.GM_LightningBolt",
            "GD_Aster_GrenadeMods.A_Item.GM_MagicMissileRare",
            "GD_Orchid_GrenadeMods.A_Item_Custom.GM_Blade",
            "GD_GrenadeMods.A_Item_Custom.GM_FusterCluck",
            "GD_GrenadeMods.A_Item_Custom.GM_KissOfDeath",
            "GD_GrenadeMods.A_Item_Custom.GM_SkyRocket",
        ]
    ),
    120: clone_item_pool("GD_Itempools.ClassModPools.Pool_ClassMod_01_Common"),
    121: clone_item_pool("GD_Itempools.ClassModPools.Pool_ClassMod_02_Uncommon"),
    122: clone_item_pool("GD_Itempools.ClassModPools.Pool_ClassMod_04_Rare"),
    123: clone_item_pool("GD_Itempools.ClassModPools.Pool_ClassMod_05_VeryRare"),
    125: construct_item_pool("BLGLegendaryClassMods",
        inv_bal_kind="InventoryBalanceDefinition",
        inv_bal_def_names=[
            # "GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Soldier_05_Legendary",
        ],
        pool_names=[
            "GD_Itempools.ClassModPools.Pool_ClassMod_06_Legendary",
            "GD_Itempools.ClassModPools.Pool_ClassMod_06_SlayerOfTerramorphous",
            # lobelia has 3 elements per character, so add it 3 times to balance
            "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All", 
            "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All",
            "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All",
        ],
    ),
    130: construct_item_pool("BLGCommonRelic", inv_bal_kind="InventoryBalanceDefinition",
        pool_names=[
            "GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
        ],
        relic_rarity="Common",
    ),
    131: construct_item_pool("BLGUnommonRelic", inv_bal_kind="InventoryBalanceDefinition",
        pool_names=[
            "GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
        ],
        relic_rarity="Uncommon",
    ),
    132: construct_item_pool("BLGRareRelic", inv_bal_kind="InventoryBalanceDefinition",
        pool_names=[
            # "GD_Itempools.ArtifactPools.Pool_Artifacts_03_Rare", # this should work but produces white relics. no clue.
            "GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
        ],
        relic_rarity="Rare",
    ),
    133: construct_item_pool("BLGVeryRareRelic", inv_bal_kind="InventoryBalanceDefinition",
        pool_names=[
            "GD_Itempools.ArtifactPools.Pool_Artifacts_03_Rare",
        ],
        relic_rarity="VeryRare",
    ),
    134: construct_item_pool("BLGETechRelic", inv_bal_kind="InventoryBalanceDefinition",
        pool_names=[
            "GD_Gladiolus_Itempools.ArtifactPools.Pool_Artifacts_Ancient_AggressionTenacity"
        ],
        inv_bal_def_names=[
            # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityAssault_VeryRare",
            # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityLauncher_VeryRare",
            # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityPistol_VeryRare",
            # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityShotgun_VeryRare",
            # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacitySMG_VeryRare",
            # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacitySniper_VeryRare",
            "GD_Gladiolus_Artifacts.A_Item.A_ElementalProficiency_VeryRare",
            "GD_Gladiolus_Artifacts.A_Item.A_ResistanceProtection_VeryRare",
            "GD_Gladiolus_Artifacts.A_Item.A_VitalityStockpile_VeryRare",
        ],
    ),
    139: construct_item_pool("BLGUniqueRelic", inv_bal_kind="InventoryBalanceDefinition",
        inv_bal_def_names=[
            "GD_Artifacts.A_Item_Unique.A_Afterburner",
            "GD_Artifacts.A_Item_Unique.A_Deputy",
            "GD_Artifacts.A_Item_Unique.A_Endowment",
            "GD_Artifacts.A_Item_Unique.A_Opportunity",
            "GD_Artifacts.A_Item_Unique.A_Sheriff",
            "GD_Artifacts.A_Item_Unique.A_VaultHunter",
            "GD_Aster_Artifacts.A_Item_Unique.A_MysteryAmulet",
        ],
    ),
    140: construct_item_pool("BLGWhitePistols",
        inv_bal_def_names=[
            "GD_Weap_Pistol.A_Weapons.Pistol_Bandit",
            "GD_Weap_Pistol.A_Weapons.Pistol_Tediore",
            "GD_Weap_Pistol.A_Weapons.Pistol_Dahl",
            "GD_Weap_Pistol.A_Weapons.Pistol_Vladof",
            "GD_Weap_Pistol.A_Weapons.Pistol_Torgue",
            "GD_Weap_Pistol.A_Weapons.Pistol_Jakobs",
            "GD_Weap_Pistol.A_Weapons.Pistol_Hyperion",
            "GD_Weap_Pistol.A_Weapons.Pistol_Maliwan", # Maliwan has to be at the end? no idea what's going on
        ]
    ),
    # return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Pistols_01_Common") # Maliwan breaks for this


    141: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Pistols_02_Uncommon"),
    142: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Pistols_04_Rare"),
    143: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare", skip_alien=True),
    144: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare_Alien"),
    145: construct_item_pool("BLGLegendaryPistols",
        src_pool_name="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_06_Legendary",
        pool_names=[
            "GD_Anemone_ItemPools.WeaponPools.Pool_Pistol_Hector_Paradise"
        ]
    ),
    149: construct_item_pool("BLGUniquePistols",
        inv_bal_def_names=[
            "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Fibber",
            "GD_Orchid_BossWeapons.Pistol.Pistol_Jakobs_ScarletsGreed",
            "GD_Aster_Weapons.Pistols.Pistol_Maliwan_3_GrogNozzle",
            "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_GwensHead",
            "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Judge",
            "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_LadyFist",
            "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Law",
            "GD_Orchid_BossWeapons.Pistol.Pistol_Maliwan_3_LittleEvie",
            "GD_Iris_Weapons.Pistols.Pistol_Torgue_3_PocketRocket",
            "GD_Sage_Weapons.Pistols.Pistol_Jakobs_3_Rex",
            "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Maliwan_3_Rubi",
            "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Teapot",
            "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Bandit_3_Tenderbox",
            "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Vladof_3_Veritas",
            # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_Starter",
            "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Dahlminator",
        ],
        pool_names=[]
    ),
    150: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_01_Common"),
    151: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_02_Uncommon"),
    152: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_04_Rare"),
    153: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare"),
    154: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare_Alien"),
    155: construct_item_pool("BLGLegendaryShotguns", 
        src_pool_name="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_06_Legendary",
        inv_bal_def_names=[
            "GD_Anemone_Weapons.Shotgun.Overcompensator.SG_Hyperion_6_Overcompensator"
        ]
    ),
    159: construct_item_pool("BLGUniqueShotguns",
        inv_bal_def_names=[
            "GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Blockhead",
            "GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Dog",
            "GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_HeartBreaker",
            "GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Hydra",
            "GD_Orchid_BossWeapons.Shotgun.SG_Bandit_3_JollyRoger",
            "GD_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_Landscaper",
            "GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Octo",
            "GD_Orchid_BossWeapons.Shotgun.SG_Jakobs_3_OrphanMaker",
            "GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_RokSalt",
            "GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_Shotgun1340",
            "GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Teeth",
            "GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_TidalWave",
            "GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_Triquetra",
            "GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Twister",
            "GD_Aster_Weapons.Shotguns.SG_Torgue_3_SwordSplosion",
            "GD_Iris_Weapons.Shotguns.SG_Hyperion_3_SlowHand",
        ],
        pool_names=[]
    ),
    160: construct_item_pool("BLGWhiteSMGs",
        inv_bal_def_names=[
            "GD_Weap_SMG.A_Weapons.SMG_Bandit",
            "GD_Weap_SMG.A_Weapons.SMG_Tediore",
            "GD_Weap_SMG.A_Weapons.SMG_Dahl",
            "GD_Weap_SMG.A_Weapons.SMG_Hyperion",
            "GD_Weap_SMG.A_Weapons.SMG_Maliwan", # Maliwan has to be at the end?
        ]
    ),
    # return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SMG_01_Common")  # has Maliwan issue.

    161: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SMG_02_Uncommon"),
    162: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SMG_04_Rare"),
    163: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SMG_05_VeryRare"),
    164: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SMG_05_VeryRare_Alien"),
    165: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SMG_06_Legendary"),
    169: construct_item_pool("BLGUniqueSMGs",
        inv_bal_def_names=[
            "GD_Weap_SMG.A_Weapons_Unique.SMG_Bandit_3_BoneShredder",
            "GD_Weap_SMG.A_Weapons_Unique.SMG_Dahl_3_Lascaux",
            "GD_Weap_SMG.A_Weapons_Unique.SMG_Gearbox_1",
            "GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Bane",
            "GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Commerce",
            "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch",
            "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_Chulainn",
            "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_GoodTouch",
            "GD_Sage_Weapons.SMG.SMG_Hyperion_3_YellowJacket",
            "GD_Orchid_BossWeapons.SMG.SMG_Dahl_3_SandHawk",
            "GD_Aster_Weapons.SMGs.SMG_Bandit_3_Orc",
            "GD_Aster_Weapons.SMGs.SMG_Barrel_Dahl_Orc",
            "GD_Aster_Weapons.SMGs.SMG_Maliwan_3_Crit",
        ],
        pool_names=[]
    ),
    170: construct_item_pool("BLGWhiteSniperRifles",
        inv_bal_def_names=[
            "GD_Weap_SniperRifles.A_Weapons.Sniper_Dahl",
            "GD_Weap_SniperRifles.A_Weapons.Sniper_Vladof",
            "GD_Weap_SniperRifles.A_Weapons.Sniper_Jakobs",
            "GD_Weap_SniperRifles.A_Weapons.Sniper_Hyperion",
            "GD_Weap_SniperRifles.A_Weapons.Sniper_Maliwan", # Maliwan has to be at the end?
        ]
    ),
    # return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_01_Common") # has Maliwan issue.

    171: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_02_Uncommon"),
    172: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_04_Rare"),
    173: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_05_VeryRare", skip_alien=True),
    174: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_05_VeryRare_Alien"),
    175: construct_item_pool(
        "BLGLegendarySnipers", 
        src_pool_name="GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_06_Legendary",
        inv_bal_def_names=[
            # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Dahl_5_Pitchfork",
            # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Vladof_5_Lyudmila",
            # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Maliwan_5_Volcano",
            # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Jakobs_5_Skullmasher",
            # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Hyperion_5_Invader",
            "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Longbow",
            "GD_Anemone_Weapons.A_Weapons_Unique.Sniper_Jakobs_3_Morde_Lt",
        ]
    ),
    179: construct_item_pool("BLGUniqueSnipers",
        inv_bal_def_names=[
            "GD_Sage_Weapons.SniperRifles.Sniper_Jakobs_3_ElephantGun",
            "GD_Orchid_BossWeapons.SniperRifles.Sniper_Maliwan_3_Pimpernel",
            "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Buffalo",
            "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Maliwan_3_ChereAmie",
            "GD_Iris_Weapons.SniperRifles.Sniper_Jakobs_3_Cobra",
            "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_FremingtonsEdge",
            "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Morningstar",
            "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Dahl_3_Sloth",
            "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Tresspasser",
            # "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Gearbox_1",

            # GD_Aster_Weapons.Snipers.SR_Dahl_4_Emerald
            # GD_Aster_Weapons.Snipers.SR_Hyperion_4_Diamond
            # GD_Aster_Weapons.Snipers.SR_Jakobs_4_Citrine
            # GD_Aster_Weapons.Snipers.SR_Maliwan_4_Aquamarine
            # GD_Aster_Weapons.Snipers.SR_Vladof_4_Garnet
        ],
        pool_names=[]
    ),
    180: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_01_Common"),
    181: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_02_Uncommon"),
    182: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_04_Rare"),
    183: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare"),
    184: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare_Alien"),
    185: construct_item_pool(
        "BLGLegendaryARs",
        src_pool_name="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_06_Legendary",
        inv_bal_def_names=[
            "GD_Aster_Weapons.AssaultRifles.AR_Bandit_3_Ogre"
        ]
    ),
    189: construct_item_pool("BLGUniqueARs",
        inv_bal_def_names=[
            "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_3_Scorpio",
            "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Jakobs_3_Stomper",
            "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Torgue_3_EvilSmasher",
            "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Vladof_3_Hail",
            "GD_Sage_Weapons.AssaultRifle.AR_Jakobs_3_DamnedCowboy",
            "GD_Sage_Weapons.AssaultRifle.AR_Bandit_3_Chopper",
            "GD_Iris_Weapons.AssaultRifles.AR_Torgue_3_BoomPuppy",
            "GD_Iris_Weapons.AssaultRifles.AR_Vladof_3_Kitten",
            "GD_Orchid_BossWeapons.AssaultRifle.AR_Jakobs_3_Stinkpot",
            "GD_Orchid_BossWeapons.AssaultRifle.AR_Vladof_3_Rapier",
            # GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_1_GBX
        ],
        pool_names=[]
    ),
    190: construct_item_pool("BLGWhiteRPGs",
        inv_bal_def_names=[
            "GD_Weap_Launchers.A_Weapons.RL_Bandit",
            "GD_Weap_Launchers.A_Weapons.RL_Tediore",
            "GD_Weap_Launchers.A_Weapons.RL_Vladof",
            "GD_Weap_Launchers.A_Weapons.RL_Torgue",
            "GD_Weap_Launchers.A_Weapons.RL_Bandit",
            "GD_Weap_Launchers.A_Weapons.RL_Maliwan", # Maliwan has to be at the end?
        ]
    ),
    # return clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Launchers_01_Common") # has Maliwan issue.
    191: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Launchers_02_Uncommon"),
    192: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Launchers_04_Rare"),
    193: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Launchers_05_VeryRare"),
    194: clone_item_pool("GD_Itempools.WeaponPools.Pool_Weapons_Launchers_05_VeryRare_Alien"),
    195: construct_item_pool(
            # issue with this one? Refusing to set array property to itself
        "BLGLegendaryRPGs",
        src_pool_name="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_06_Legendary",
        inv_bal_def_names=[
            "GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_Alien_Norfleet"
        ]
    ),
    199: construct_item_pool("BLGUniqueRPGs",
        inv_bal_def_names=[
            "GD_Weap_Launchers.A_Weapons_Unique.RL_Bandit_3_Roaster",
            "GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_3_TheHive",
            "GD_Weap_Launchers.A_Weapons_Unique.RL_Torgue_3_Creamer",
            "GD_Orchid_BossWeapons.Launcher.RL_Torgue_3_12Pounder",
        ],
        pool_names=[]
    ),

    # "Common GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_01_Common",
    # "Uncommon GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_02_Uncommon",
    # "Rare GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_04_Rare",
    # "VeryRare GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_05_VeryRare",
    # "Legendary GrenadeMod": "GD_Itempools.GrenadeModPools.Pool_GrenadeMods_06_Legendary",

    # "Common ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_01_Common",
    # "Uncommon ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_02_Uncommon",
    # "Rare ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_04_Rare",
    # "VeryRare ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_05_VeryRare",
    # "Legendary ClassMod": "GD_Itempools.ClassModPools.Pool_ClassMod_06_Legendary",
    
    # "Common Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
    # "Uncommon Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_02_Uncommon",
    # "Rare Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_03_Rare",
    # "VeryRare Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_04_VeryRare",
    # "Legendary Relic": "GD_Itempools.ArtifactPools.Pool_Artifacts_05_Legendary",

    # "Common Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_01_Common',
    # "Uncommon Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_02_Uncommon', 
    # "Rare Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_04_Rare',
    # "VeryRare Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare',
    # "E-Tech Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare_Alien',
    # "Legendary Pistol": 'GD_Itempools.WeaponPools.Pool_Weapons_Pistols_06_Legendary',

    # "Common Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_01_Common',
    # "Uncommon Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_02_Uncommon',
    # "Rare Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_04_Rare',
    # "VeryRare Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare',
    # "E-Tech Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare_Alien',
    # "Legendary Shotgun": 'GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_06_Legendary',

    # "Common SMG": 'GD_Itempools.WeaponPools.Pool_Weapons_SMG_01_Common',
    # "Uncommon SMG": 'GD_Itempools.WeaponPools.Pool_Weapons_SMG_02_Uncommon',
    # "Rare SMG": 'GD_Itempools.WeaponPools.Pool_Weapons_SMG_04_Rare',
    # "VeryRare SMG": 'GD_Itempools.WeaponPools.Pool_Weapons_SMG_05_VeryRare',
    # "E-Tech SMG": 'GD_Itempools.WeaponPools.Pool_Weapons_SMG_05_VeryRare_Alien',
    # "Legendary SMG": 'GD_Itempools.WeaponPools.Pool_Weapons_SMG_06_Legendary',

    # "Common SniperRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_01_Common',
    # "Uncommon SniperRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_02_Uncommon',
    # "Rare SniperRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_04_Rare',
    # "VeryRare SniperRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_05_VeryRare',
    # "E-Tech SniperRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_05_VeryRare_Alien',
    # "Legendary SniperRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_06_Legendary',

    # "Common AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_01_Common',
    # "Uncommon AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_02_Uncommon',
    # "Rare AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_04_Rare',
    # "VeryRare AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare',
    # "E-Tech AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare_Alien',
    # "Legendary AssaultRifle": 'GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_06_Legendary',

    # "Common RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_01_Common',
    # "Uncommon RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_02_Uncommon',
    # "Rare RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_04_Rare',
    # "VeryRare RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_05_VeryRare',
    # "E-Tech RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_05_VeryRare_Alien',
    # "Legendary RocketLauncher": 'GD_Itempools.WeaponPools.Pool_Weapons_Launchers_06_Legendary',
}
'''