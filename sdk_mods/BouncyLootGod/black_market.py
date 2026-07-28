import unrealsdk
import unrealsdk.unreal as unreal
import random
from mods_base import get_pc, hook, Game
from ui_utils import show_chat_message
from unrealsdk.hooks import Type, Block, prevent_hooking_direct_calls
from BouncyLootGod.state import ApItemMesh, game_is_bl2, game_is_tps, get_globals
from BouncyLootGod.bl2.loot_pools import spawn_gear

def level_my_gear():
    pc = get_pc()
    # could use pc.GetFullInventory([])
    current_level = pc.PlayerReplicationInfo.ExpLevel
    inventory_manager = pc.GetPawnInventoryManager()

    if not inventory_manager:
        show_chat_message('no inventory, skipping')
        return

    backpack = inventory_manager.Backpack
    if not backpack:
        show_chat_message('no backpack loaded')
        return

    # go through backpack
    for item in backpack:
        try:
            # skip skyrocket, it gets deleted for some reason
            if item.DefinitionData.ItemDefinition.Name == "GrenadeMod_SkyRocket":
                continue
        except:
            pass
        item.DefinitionData.ManufacturerGradeIndex = current_level
        item.DefinitionData.GameStage = current_level
        with prevent_hooking_direct_calls():
            item.InitializeFromDefinitionData(item.DefinitionData, None)

        # item.ExpLevel = current_level
        # item.GameStage = current_level


    # go through item chain (relic, classmod, grenade, shield)
    item = inventory_manager.ItemChain
    while item:
        # skip skyrocket, it gets deleted for some reason
        if item.DefinitionData.ItemDefinition.Name != "GrenadeMod_SkyRocket":
            item.DefinitionData.ManufacturerGradeIndex = current_level
            item.DefinitionData.GameStage = current_level
            with prevent_hooking_direct_calls():
                item.InitializeFromDefinitionData(item.DefinitionData, None)
        item = item.Inventory

    # go through equipment slots
    for i in [1, 2, 3, 4]:
        weapon = inventory_manager.GetWeaponInSlot(i)
        if weapon:
            weapon.DefinitionData.ManufacturerGradeIndex = current_level
            weapon.DefinitionData.GameStage = current_level
            with prevent_hooking_direct_calls():
                weapon.InitializeFromDefinitionData(weapon.DefinitionData, None)

    show_chat_message("gear set to level " + str(current_level))
    return

bm_price = 50
@hook("WillowGame.WillowVendingMachineBlackMarket:GetSellingPriceForInventory")
def black_market_get_price(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if args.InventoryForSale.DefinitionData.ItemDefinition.Name == "INV_SDU_Bank":
        return
    return Block, bm_price

if game_is_tps():
    bm_purchasables = [
        ("Shield Package", "Prop_Co_ShiftItems.Meshes.Paint", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"),
        ("Class Mod Package", "Prop_Co_ShiftItems.Meshes.Co_ShiftItems_BoxofGears", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"),
        ("Grenade Mod Package", "Prop_Co_ShiftItems.Meshes.Shift_Candy", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"),
        ("Oz Kit Package", "Prop_Co_Oxygencanister.Mesh.Co_Oxygencanister", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"),
        ("Glitch Package", "Prop_Co_ShiftItems.Meshes.Co_DahlShift_SatellitePhone", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"),
        ("Laser Package", "Prop_Details.Meshes.GiftBow", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"),
        ("RocketLauncher Package", "Prop_Details.Meshes.BeerBottle", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"), #TODO: Replace with moonstone loot when implemented as filler
        ("Money", "Prop_Details.Meshes.Crumpets", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"),
    ]
else:
    bm_purchasables = [
        ("E-Tech Package", "prop_lightfixtures.Meshes.WallLight_02", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
        ("Shield Package", "Prop_Tires.RubberTire", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
        ("Rigged Slots (1 Spin)", "Prop_Signs_02.Meshes.SanctuaryClaptrap", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
        ("Grenade Mod Package", "Prop_Papers.Meshes.CrumpledPaper", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
        # ("Tina COM Package", "Prop_Details.Meshes.Radio", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
        ("Gemstone Package", "Prop_Details.Books", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
        ("Seraph Crystals", "Prop_Bank.Meshes.Vault", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
        ("Money", "Prop_Pickups.Meshes.Money_02", "Prop_Pickups.Materials.Eridium_Pickups_Bar"),
    ]

def change_bm_inventory(bmvm):
    if bmvm is None:
        return
    pc = get_pc()
    blg = get_globals()
    item_mesh_details = blg.vending_item_mesh or ApItemMesh(
        item_definition="GD_Assassin_Items_Aster.Assassin.Head_ZeroAster",
        mesh="Prop_Details.Meshes.PizzaBoxWhole",
        material="Prop_Details.Materials.Mati_PizzaBox",
        package="SanctuaryAir_Dynamic"
    )
    sample_def = unrealsdk.find_object("UsableCustomizationItemDefinition", item_mesh_details.item_definition)
    def setup_item(item, purchasable_data):
        blg = get_globals()
        name = purchasable_data[0] if purchasable_data else "Blank"
        mesh = unrealsdk.find_object("StaticMesh", purchasable_data[1] if purchasable_data else item_mesh_details.mesh)
        mat = unrealsdk.find_object("MaterialInstanceConstant", purchasable_data[2] if purchasable_data else item_mesh_details.material)

        item_def_name = f"archi_bm_def_{name.replace(' ', '_').replace(':', '')}"
        item_def = unrealsdk.construct_object("UsableCustomizationItemDefinition", blg.package, item_def_name, 0, sample_def)
        item_def.OverrideMaterial = mat
        item_def.NonCompositeStaticMesh = mesh
        item_def.ItemName = f"Black Market: {name}"
        item_def.CustomPresentations = []
        item_def.bPlayerUseItemOnPickup = True 
        item_def.bIsConsumable = True
        item_def.BaseRarity.BaseValueConstant = 500.0 
        item_def.UIMeshRotation = unrealsdk.make_struct("Rotator", Pitch = -134, Yaw = -14219, Roll = -7164)
        item_def.FormOfCurrency = 1 # unrealsdk.find_enum("ECurrencyType")["CURRENCY_Eridium"]
        
        item.InitializeFromDefinitionData(
            unrealsdk.make_struct("ItemDefinitionData", ItemDefinition=item_def),
            None
        )

    inv_list = bmvm.GetInventoryList([], pc)
    inv_items = inv_list[1]
    i = 0
    for inv in inv_items:
        if inv.Item.DefinitionData.ItemDefinition.Name == "INV_SDU_Bank":
            continue
        purchasable_data = bm_purchasables[i] if i < len(bm_purchasables) else None
        i += 1
        setup_item(inv.Item, purchasable_data)

    featured = bmvm.GetFeaturedItem(pc)
    if featured and featured.Item:
        if game_is_tps():
            setup_item(featured.Item, ("Level My Gear", "Prop_Details.Meshes.PizzaBoxWhole", "FX_CREA_PrimalBeast.Materials.Mati_Ice_Chunk"))
        else:
            setup_item(featured.Item, ("Level My Gear", "Prop_Pickups.Meshes.EridiumContainer", "Prop_Pickups.Materials.Eridium_Pickups_Bar"))
        


@hook("WillowGame.BlackMarketDefinition:CurrentLevelIsBelowMaxForPlayer")
def current_level_is_below_max(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # make black market items always appear
    # TODO this should probably not override for bank sdu
    return Block, True

@hook("WillowGame.WillowVendingMachineBase:ResetInventory")
def reset_black_market(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if obj.Class.Name != "WillowVendingMachineBlackMarket":
        return
    change_bm_inventory(obj)


@hook("WillowGame.WillowInteractiveObject:UseObject")
def use_black_market(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if obj.Class.Name != "WillowVendingMachineBlackMarket":
        return

    # get_pc().WorldInfo.GRI.MissionTracker.UpdateObjective(unrealsdk.find_object("MissionObjectiveDefinition", "GD_Episode04.M_Ep4_WelcomeToSanctuary:BuyFuelCell"))
    change_bm_inventory(obj)

@hook("WillowGame.WillowVendingMachineBlackMarket:PlayerBuyItem")
def black_market_buy_item(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    pc = get_pc()
    blg = get_globals()

    bought_item = args.Item
    name = bought_item.ItemName
    if not name.startswith("Black Market: "):
        return

    # take money, hook does not trigger if can't afford
    pc.PlayerReplicationInfo.AddCurrencyOnHand(1, -bm_price)

    name = name.split("Black Market: ")[-1]


    show_chat_message(f"Purchased {name}!")
    spawns = []
    if name == "E-Tech Package":
        spawns = random.sample(["E-Tech Relic", "E-Tech Pistol", "E-Tech Shotgun", "E-Tech SMG", "E-Tech SniperRifle", "E-Tech AssaultRifle", "E-Tech RocketLauncher"], 3)
    elif name == "Shield Package":
        spawns = ["Legendary Shield", "VeryRare Shield", "Unique Shield"]
    elif name == "Grenade Mod Package":
        spawns = ["Legendary GrenadeMod", "Seraph GrenadeMod", "VeryRare GrenadeMod"]
    elif name == "Money":
        pc.PlayerReplicationInfo.AddCurrencyOnHand(0, blg.money_cap)
    elif name == "Seraph Crystals":
        spawns = ["Seraph Crystals"] * 80
        # pc.PlayerReplicationInfo.AddCurrencyOnHand(2, 80)
    elif name == "Gemstone Package":
        spawns = random.sample(["Gemstone Pistol", "Gemstone Shotgun", "Gemstone SMG", "Gemstone SniperRifle", "Gemstone AssaultRifle" ], 3)
    elif name == "Glitch Package":
        spawns = random.sample(["Glitch Pistol", "Glitch Laser", "Glitch Shotgun", "Glitch SMG", "Glitch SniperRifle", "Glitch AssaultRifle", "Glitch RocketLauncher"], 3)
    elif name == "RocketLauncher Package":
        spawns = ["Legendary RocketLauncher", "Rare RocketLauncher", "VeryRare RocketLauncher"]
    elif name == "Laser Package":
        spawns = ["Legendary Laser", "Rare Laser", "VeryRare Laser"]
    elif name == "Oz Kit Package":
        spawns = ["Legendary Oz Kit", "Rare Oz Kit", "VeryRare Oz Kit"]
    elif name == "Level My Gear":
        level_my_gear()
    elif name == "Rigged Slots (1 Spin)":
        pc.ConsoleCommand("set gd_slotmachine.SlotMachine:BehaviorProviderDefinition_0.Behavior_RandomBranch_34 Conditions (0,0,0,0,100,0,0,0,0,0,0,0)")
        # TODO: can we do this without ConsoleCommand
    else:
        show_chat_message("Option not implemented")
        pc.PlayerReplicationInfo.AddCurrencyOnHand(1, bm_price)
        print(f"unknown black market purchase: {name}")

    # pc.PlayerReplicationInfo.AddCurrencyOnHand(4, 33) # torgue tokens
    if game_is_tps():
        spawn_loc = {"X": obj.Location.X-600, "Y": obj.Location.Y - 600, "Z": obj.Location.Z + 500}
    else:
        spawn_loc = {"X": obj.Location.X, "Y": obj.Location.Y - 1000, "Z": obj.Location.Z + 500}
    for s in spawns:
        spawn_loc["X"] += 20
        spawn_gear(s, override_loc=spawn_loc)

    # for the Whaddaya Buyin challenge and Plan B mission
    player_stats_list = unrealsdk.find_all("WillowGame.WillowPlayerStats") # coop host will see other player's in this list.
    my_stats = next((x for x in player_stats_list if x.Owner == pc), player_stats_list[-1])
    my_stats.IncrementIntStat("STAT_PLAYER_NUM_BLACK_MARKET_ITEMS_PURCHASED", 1)
    my_stats.IncrementIntStat("STAT_PLAYER_INVENTORY_PURCHASED_WITH_ERIDIUM", 1)
    if game_is_tps():
        get_pc().WorldInfo.GRI.MissionTracker.UpdateObjective(unrealsdk.find_object("MissionObjectiveDefinition", "GD_Co_Chapter03.M_Co_Ch03_Concordia:16_BuyUpgrade"))
    else:
        get_pc().WorldInfo.GRI.MissionTracker.UpdateObjective(unrealsdk.find_object("MissionObjectiveDefinition", "GD_Episode04.M_Ep4_WelcomeToSanctuary:BuyFuelCell"))

    return Block

@hook("WillowGame.InteractiveObjectDefinition:OnUsedBy", Type.POST)
def reset_slot_machine(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if str(obj) == "InteractiveObjectDefinition'gd_slotmachine.SlotMachine'":
        get_pc().ConsoleCommand("set gd_slotmachine.SlotMachine:BehaviorProviderDefinition_0.Behavior_RandomBranch_34 Conditions (40.00, 30.00, 3.00, 0.30, 0.03, 5.00, 1.50, 0.45, 50.00, 15.00, 10.00, 40.00)")


if game_is_tps():
    black_market_hooks = [
        use_black_market,
        black_market_get_price,
        reset_black_market,
        black_market_buy_item,
        current_level_is_below_max,
    ]
elif game_is_bl2():
    black_market_hooks = [
        use_black_market,
        black_market_get_price,
        reset_black_market,
        black_market_buy_item,
        current_level_is_below_max,
        reset_slot_machine,
    ]
else:
    black_market_hooks = []