import unrealsdk
import unrealsdk.unreal as unreal
from mods_base import Game, hook
from BouncyLootGod.archi_data import loc_name_to_id
from BouncyLootGod.state import get_globals, get_or_create_package, ApItemMesh
if Game.get_current().name == "TPS":
    from BouncyLootGod.bl_tps.vending_machines import vending_machine_position_to_name
else:
    from BouncyLootGod.bl2.vending_machines import vending_machine_position_to_name


def get_vending_machine_pos_str(wvm):
    # old way: f"{str(wvm.Outer)}~{str(wvm.Location.X)},{str(wvm.Location.Y)}"
    return f"{int(wvm.Location.X)},{int(wvm.Location.Y)}"

def reroll_featured_to_non_weapon(vending_machine):
    if Game.get_current().name == "TPS":
        if vending_machine.FormOfCurrency == 0:
            pool = unrealsdk.find_object("ItemPoolDefinition", "GD_ItemPools_Shop.WeaponPools.Shoppool_IOTD_WeaponMachine")
        else:
            return
    else:
        if vending_machine.FormOfCurrency == 4:
            pool = unrealsdk.find_object("ItemPoolDefinition", "GD_Iris_ItemPools.TorgueTokenVendor.Shoppool_FeaturedItem_WeaponMachine")
        elif vending_machine.FormOfCurrency == 0:
            pool = unrealsdk.find_object("ItemPoolDefinition", "GD_ItemPools_Shop.WeaponPools.Shoppool_FeaturedItem_WeaponMachine")
        else:
            return

    pool_prob_backup = [bi.Probability.BaseValueConstant for bi in pool.BalancedItems]

    # all of the pools have non-weapons for the last entry, modify the probabilities
    for bi in pool.BalancedItems[:-1]:
        bi.Probability.BaseValueConstant = 0
    pool.BalancedItems[-1].Probability.BaseValueConstant = 100 

    # reroll once
    vending_machine.ResetInventory()

    # restore original probabilities
    for i, prob in enumerate(pool_prob_backup):
        pool.BalancedItems[i].Probability.BaseValueConstant = prob


@hook("WillowGame.WillowInteractiveObject:UseObject")
def use_vending_machine(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if obj.Class.Name != "WillowVendingMachine":
        return
    blg = get_globals()
    if blg.settings.get("vending_machines") == 0:
        # skip if vending machine checks are off
        # TODO new include_locations settings could include vending machines with the vending_machines setting off
        return
    # TODO: settings option to always remove iotd

    pos_str = get_vending_machine_pos_str(obj)
    check_name = vending_machine_position_to_name.get(pos_str)
    if not check_name:
        # log_to_file("opened unknown Vending Machine: " + pos_str)
        # show_chat_message("opened unknown Vending Machine: " + pos_str)
        return

    loc_id = loc_name_to_id.get(check_name)
    if loc_id is None:
        return

    if loc_id in blg.locations_checked:
        return
    blg.active_vend = obj
    blg.active_vend_price = obj.FixedFeaturedItemCost
    if True:
        for loot_configuration in obj.Loot:
            if loot_configuration.ConfigurationName == "FeaturedItem":
                # print("Found FeaturedItem config")
                item_pool = unrealsdk.construct_object("ItemPoolDefinition", blg.package, "AP_Vending_Featured_Item_Pool")
                item_pool.MinGameStageRequirement = None
                probability = unrealsdk.make_struct("AttributeInitializationData", BaseValueConstant=1, BaseValueScaleConstant=1)
                if Game.get_current().name == "TPS":
                    ibd = "GD_Baroness_Items_crocus.BalanceDefs.Baroness_Head_Baron002"
                else:
                    ibd = "GD_Orchid_Shields.A_Item_Custom.S_BladeShield" #might want a different IBD here 
                inv_bal_def = unrealsdk.find_object("InventoryBalanceDefinition", ibd)
                balanced_item = unrealsdk.make_struct("BalancedInventoryData", InvBalanceDefinition=inv_bal_def, Probability=probability, bDropOnDeath=True)
                item_pool.BalancedItems.append(balanced_item)
                config = loot_configuration.ItemAttachments[0]
                item_pool_backup = config.ItemPool
                config.ItemPool = item_pool
                obj.ResetInventory()
                config.ItemPool = item_pool_backup
    else:
        if obj.FeaturedItem is None and Game.get_current().name == "TPS":
            for loot_configuration in obj.Loot:
                if loot_configuration.ConfigurationName == "FeaturedItem":
                    item_pool = unrealsdk.construct_object("ItemPoolDefinition", blg.package, "AP_TPS_VENDING_FEATURED_ITEM_POOL")
                    item_pool.MinGameStageRequirement = None
                    probability = unrealsdk.make_struct("AttributeInitializationData", BaseValueConstant=1, BaseValueScaleConstant=1)
                    inv_bal_def = unrealsdk.find_object("InventoryBalanceDefinition", "GD_Baroness_Items_crocus.BalanceDefs.Baroness_Head_Baron002")
                    balanced_item = unrealsdk.make_struct("BalancedInventoryData", InvBalanceDefinition=inv_bal_def, Probability=probability, bDropOnDeath=True)
                    item_pool.BalancedItems.append(balanced_item)
                    config = loot_configuration.ItemAttachments[0]
                    item_pool_backup = config.ItemPool
                    config.ItemPool = item_pool
                    obj.ResetInventory()
                    config.ItemPool = item_pool_backup
    if obj.FormOfCurrency == 0:
        obj.FixedFeaturedItemCost = 100
    else:
        # Torgue and Seraph vendors
        obj.FixedFeaturedItemCost = 10


    # force the featured item to not be a weapon
    if obj.FeaturedItem.Class.Name == "WillowWeapon":
        print("it's a weapon somehow.")
        reroll_featured_to_non_weapon(obj)

    if obj.FeaturedItem.Class.Name == "WillowWeapon":
        print("it's still a weapon somehow.")
        # make a broken/empty weapon
        w_def = obj.FeaturedItem.DefinitionData
        obj.FeaturedItem.InitializeFromDefinitionData(
            unrealsdk.make_struct("WeaponDefinitionData",
                WeaponTypeDefinition=w_def.WeaponTypeDefinition,
                BalanceDefinition=w_def.BalanceDefinition,
            ),
            None
        )
        obj.FeaturedItem.ItemName = "AP Check: " + check_name
        return

    mesh_def = ApItemMesh(
        item_definition="GD_Assassin_Items_Aster.Assassin.Head_ZeroAster",
        mesh="Prop_Details.Meshes.PizzaBoxWhole",
        material="Prop_Details.Materials.Mati_PizzaBox",
        package="SanctuaryAir_Dynamic",
        loot_pool="GD_Itempools.EarlyGame.Pool_Knuckledragger_Pistol"
    )
    if blg.vending_item_mesh:
        mesh_def = blg.vending_item_mesh
    sample_def = unrealsdk.find_object("UsableCustomizationItemDefinition", mesh_def.item_definition)
    item_def = unrealsdk.construct_object("UsableCustomizationItemDefinition", blg.package, "archi_venditem_def", 0, sample_def)

    try:
        pizza_mesh = unrealsdk.find_object("StaticMesh", mesh_def.mesh)
    except:
        unrealsdk.load_package(mesh_def.package)
        pizza_mesh = unrealsdk.find_object("StaticMesh", mesh_def.mesh)

    item_def.NonCompositeStaticMesh = pizza_mesh
    item_def.ItemName = "AP Check: " + check_name
    item_def.CustomPresentations = []
    item_def.bPlayerUseItemOnPickup = True # allows pickup with full inventory (i think)
    item_def.bIsConsumable = True
    try:
        item_def.OverrideMaterial = unrealsdk.find_object("MaterialInstanceConstant", mesh_def.material)
    except:
        item_def.OverrideMaterial = None
    item_def.BaseRarity.BaseValueConstant = 500.0 # teal, like mission/pearl
    item_def.UIMeshRotation = unrealsdk.make_struct("Rotator", Pitch = -134, Yaw = -14219, Roll = -7164)
    obj.FeaturedItem.InitializeFromDefinitionData(
        unrealsdk.make_struct("ItemDefinitionData", ItemDefinition=item_def),
        None
    )
