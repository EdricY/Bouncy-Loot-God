
import unrealsdk
from mods_base import Game, SliderOption
from BouncyLootGod.state import get_globals, ApItemMesh
from BouncyLootGod.archi_data import loc_name_to_id
from BouncyLootGod.traps import is_trap_pawn_def

if Game.get_current().name == "TPS":
    from BouncyLootGod.bl_tps.enemies import enemy_class_to_loc_name, generic_enemy_lookup
else:
    from BouncyLootGod.bl2.enemies import enemy_class_to_loc_name, generic_enemy_lookup

def create_pizza_item_pool(check_name):
    blg = get_globals()
    ibd_default = ApItemMesh(
        item_definition="GD_DefaultProfiles.IntroEchos.BD_SoldierIntroEcho",
        usable_item_definition="GD_DefaultProfiles.IntroEchos.ID_SoldierIntroECHO",
        mesh="Prop_Details.Meshes.PizzaBoxWhole",
        package="SanctuaryAir_Dynamic",
        loot_pool="GD_Itempools.EarlyGame.Pool_Knuckledragger_Pistol"
    )
    if blg.drop_item_mesh:
        ibd_default = blg.drop_item_mesh
    sample_inv = unrealsdk.find_object("InventoryBalanceDefinition", ibd_default.item_definition)
    inv = unrealsdk.construct_object(
        "InventoryBalanceDefinition",
        blg.package,
        "archi_item_" + check_name,
        0,
        sample_inv
    )
    # return
    item_def = unrealsdk.construct_object(
        "UsableItemDefinition",
        blg.package,
        "archi_def_" + check_name,
        0,
        unrealsdk.find_object("UsableItemDefinition", ibd_default.usable_item_definition or ibd_default.item_definition)
    )
    inv.InventoryDefinition = item_def
    try:
        pizza_mesh = unrealsdk.find_object("StaticMesh", ibd_default.mesh)
    except:
        unrealsdk.load_package(ibd_default.package)
        pizza_mesh = unrealsdk.find_object("StaticMesh", ibd_default.mesh)

    if ibd_default.material:
        try:
            item_def.OverrideMaterial = unrealsdk.find_object("MaterialInstanceConstant", ibd_default.material)
        except:
            unrealsdk.load_package(ibd_default.package)
            item_def.OverrideMaterial = unrealsdk.find_object("MaterialInstanceConstant", ibd_default.material)
    
    # pizza_mesh.ObjectFlags |= ObjectFlags.KEEP_ALIVE
    item_def.NonCompositeStaticMesh = pizza_mesh
    item_def.ItemName = "AP Check: " + check_name
    item_def.BaseRarity.BaseValueConstant = 500.0 # teal, like mission/pearl
    # item_def.BaseRarity.BaseValueConstant = 5 # orange
    item_def.CustomPresentations = []
    item_def.bPlayerUseItemOnPickup = True # allows pickup with full inventory (i think)
    item_def.bDisallowAIFromGrabbingPickup = True

    item_pool = unrealsdk.construct_object(
        "ItemPoolDefinition",
        blg.package,
        "archi_pool_" + check_name,
        0,
        unrealsdk.find_object("ItemPoolDefinition", ibd_default.loot_pool)
    )
    # add our new item to the pool
    item_pool.BalancedItems[0].InvBalanceDefinition = inv
    return item_pool

def setup_check_drop(check_name, ai_pawn_bd=None, behavior_spawn_items=None, chance=1.0, skip_already_checked=True):
    if not ai_pawn_bd and not behavior_spawn_items:
        print("don't know where to put check: " + check_name)
        return
    blg = get_globals()
    if loc_name_to_id[check_name] in blg.locations_checked and skip_already_checked:
        return

    item_pool = create_pizza_item_pool(check_name)
    prob = unrealsdk.make_struct(
        "AttributeInitializationData",
        BaseValueConstant=chance,
        BaseValueAttribute=None,
        InitializationDefinition=None,
        BaseValueScaleConstant=1.000000
    )
    item_pool_info = unrealsdk.make_struct(
        "ItemPoolInfo",
        ItemPool=item_pool,
        PoolProbability=prob
    )

    # add to enemy
    # This can add the item multiple times if this function is called multiple times. But the item pools seem to be reset when re-entering the area
    # TODO search through loot pool for if it exists already.
    if ai_pawn_bd:
        if len(ai_pawn_bd.DefaultItemPoolList) > 0:
            ai_pawn_bd.DefaultItemPoolList.append(item_pool_info)
        else:
            for pt in ai_pawn_bd.PlayThroughs:
                pt.CustomItemPoolList.append(item_pool_info)

    elif behavior_spawn_items:
        behavior_spawn_items.ItemPoolList.append(item_pool_info)

def setup_generic_mob_drops():
    blg = get_globals()
    
    skip_already_checked=True

    all_pawns = unrealsdk.find_all("AIPawnBalanceDefinition")
    all_pawns = [p for p in all_pawns if not is_trap_pawn_def(p)]

    if oid_generic_drop_chance_override.value != 0:
        chance = oid_generic_drop_chance_override.value / 100
        skip_already_checked=False
    else:
        if blg.settings.get("generic_mob_checks", 0) == 0:
            return
        chance = blg.settings.get("generic_mob_checks", 5) * 0.01
    # chance = 1

    for pawn in all_pawns:
        pawn_str = str(pawn).lower()
        if pawn.Champion:
            setup_check_drop("Generic: Badass", pawn, chance=chance)
        for generic_enemy, search_str in generic_enemy_lookup.items():
            if search_str in pawn_str:
                # skip some special cases
                if generic_enemy == "Generic: Thresher" and "tentacle" in pawn_str:
                    continue
                # print(f"{search_str} {pawn_str}")
                setup_check_drop(generic_enemy, pawn, chance=chance, skip_already_checked=skip_already_checked)

oid_generic_drop_chance_override: SliderOption = SliderOption(
    identifier="Generic Drop Chance (Debug)",
    value=0,
    min_value=0,
    max_value=100,
    step=1,
    description=(
        "Override your current drop chance for Generic Item Drops. After changing the drop chance, either save quit and reload or move to a new area to enable the new drop chance. Set to 0 for your default set chance."
    )
)
