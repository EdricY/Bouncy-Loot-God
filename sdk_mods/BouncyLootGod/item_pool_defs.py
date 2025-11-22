import unrealsdk
from ui_utils import show_chat_message


# orange = unrealsdk.make_struct("Color", R=128, G=64, B=0, A=255)

def setup_check_drop(blg, check_name, ai_pawn_bd):
    sample_inv = unrealsdk.find_object("InventoryBalanceDefinition", "GD_DefaultProfiles.IntroEchos.BD_SoldierIntroEcho")
    inv = unrealsdk.construct_object(
        "InventoryBalanceDefinition",
        blg.package,
        "archi_item_" + check_name,
        0x400004000,
        sample_inv
    )
    item_def = unrealsdk.construct_object(
        "UsableItemDefinition",
        blg.package,
        "archi_def_" + check_name,
        0x400004000,
        unrealsdk.find_object("UsableItemDefinition", "GD_DefaultProfiles.IntroEchos.ID_SoldierIntroECHO")
        # unrealsdk.find_object("InventoryBalanceDefinition", "GD_Assassin_Items_Aster.BalanceDefs.Assassin_Head_ZeroAster")
    )
    inv.InventoryDefinition = item_def
    item_def.NonCompositeStaticMesh = blg.pizza_mesh
    item_def.ItemName = "AP Check: " + check_name
    # item_def.BaseRarity.BaseValueConstant = 500.0 # teal, like mission/pearl
    item_def.BaseRarity.BaseValueConstant = 5 # orange
    item_def.CustomPresentations = []
    item_def.bPlayerUseItemOnPickup = True # allows pickup with full inventory (i think)
    item_def.bDisallowAIFromGrabbingPickup = True

    item_pool = unrealsdk.construct_object(
        "ItemPoolDefinition",
        blg.package,
        "archi_pool_" + check_name,
        0x400004000,
        unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.EarlyGame.Pool_Knuckledragger_Pistol")
    )
    # add our new item to the pool
    item_pool.BalancedItems[0].InvBalanceDefinition = inv
    prob = unrealsdk.make_struct(
        "AttributeInitializationData",
        BaseValueConstant=100.000000,
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
    if len(ai_pawn_bd.DefaultItemPoolList) > 0:
        ai_pawn_bd.DefaultItemPoolList.append(item_pool_info)
    else:
        for pt in ai_pawn_bd.PlayThroughs:
            pt.CustomItemPoolList.append(item_pool_info)

def modify_claptraps_place(blg):
    knuck = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_KnuckleDragger")
    setup_check_drop(blg, "Knuckle Dragger", knuck)
    print("Claptrap's Place Done")

def modify_southern_shelf(blg):
    flynt = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.Unique.PawnBalance_Flynt")
    setup_check_drop(blg, "Captain Flynt", flynt)

    boombewm = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Marauder.Balance.PawnBalance_BoomBoom")
    setup_check_drop(blg, "Boom Bewm", boombewm)
    print("SS done")

def modify_southern_shelf_bay(blg):
    midgemong = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_Warmong")
    setup_check_drop(blg, "Midgemong", midgemong)
    print("SS Bay done")

def modify_frostburn(blg):
    scorch = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_SpiderAnt.Balance.Unique.PawnBalance_SpiderantScorch")
    setup_check_drop(blg, "Scorch", scorch)
    clayton = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_IncineratorVanya_Combat")
    setup_check_drop(blg, "Incinerator Clayton", clayton)
    print("Frostburn done")

def modify_three_horns_divide(blg):
    savagelee = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_SavageLee")
    setup_check_drop(blg, "Savage Lee", savagelee)
    boll = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Z1_InMemoriamData.Balance.PawnBalance_Boll")
    setup_check_drop(blg, "Boll", boll)
    print("ThreeHornsDivide done")

def modify_three_horns_valley(blg):
    docmercy = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.Unique.PawnBalance_MrMercy")
    setup_check_drop(blg, "Doc Mercy", docmercy)

    badmaw = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.PawnBalance_BadMaw")
    setup_check_drop(blg, "Bad Maw", badmaw)

    print("ThreeHornsValley done")

def modify_southpaw(blg):
    # oney = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Marauder.Balance.Unique.PawnBalance_Assassin1")
    # setup_check_drop(blg, "Assassin Oney", oney)
    # wot = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.Unique.PawnBalance_Assassin2")
    # setup_check_drop(blg, "Assassin Wot", wot)
    # reeth = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_Assassin3")
    # setup_check_drop(blg, "Assassin Reeth", reeth)
    rouf = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Assassin4")
    setup_check_drop(blg, "Assassin Rouf", rouf)
    print("southpaw done")

def modify_dust(blg):
    gettle = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Engineer.Balance.Unique.PawnBalance_Gettle")
    setup_check_drop(blg, "Gettle", gettle)
    blackqueen = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_SpiderAnt.Balance.Unique.PawnBalance_SpiderantBlackQueen")
    setup_check_drop(blg, "Black Queen", blackqueen)
    print("Dust done")

def modify_bloodshot(blg):
    madmike = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.Unique.PawnBalance_MadMike")
    setup_check_drop(blg, "Mad Mike", madmike)
    print("Bloodshot done")

def modify_bloodshot_ramparts(blg):
    w4rd3n = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Constructor.Balance.Unique.PawnBalance_ConstructorRoland")
    setup_check_drop(blg, "W4R-D3N", w4rd3n)
    print("Bloodshot Ramparts done")

def modify_caustic_caverns():
    pass

def modify_oasis():
    pass

def modify_digi_peak():
    pass

def modify_heros_pass():
    pass

def modify_tundra_express():
    pass

pool_modifications = {
  "glacial_p": modify_claptraps_place,
  "southernshelf_p": modify_southern_shelf,
  "cove_p": modify_southern_shelf_bay,
  "ice_p": modify_three_horns_divide,
  "frost_p": modify_three_horns_valley,
  "southpawfactory_p": modify_southpaw,
  "icecanyon_p": modify_frostburn,
  "interlude_p": modify_dust,
  "dam_p": modify_bloodshot,
  "damtop_p": modify_bloodshot_ramparts,

  "caverns_p": modify_caustic_caverns,
  "orchid_oasistown_p": modify_oasis,
  "testingzone_p": modify_digi_peak,
  "finalbossascent_p": modify_heros_pass,
  "tundraexpress_p": modify_tundra_express,
}
