import unrealsdk
from ui_utils import show_chat_message


# orange = unrealsdk.make_struct("Color", R=128, G=64, B=0, A=255)

def setup_check_drop(blg, check_name, ai_pawn_bd):
    sample_inv = unrealsdk.find_object("InventoryBalanceDefinition", "GD_DefaultProfiles.IntroEchos.BD_SoldierIntroEcho")
    # unrealsdk.find_object("InventoryBalanceDefinition", "GD_Assassin_Items_Aster.BalanceDefs.Assassin_Head_ZeroAster")
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
        unrealsdk.find_object("UsableItemDefinition", "GD_DefaultProfiles.IntroEchos.ID_SoldierIntroECHO")
    )
    inv.InventoryDefinition = item_def
    unrealsdk.load_package("SanctuaryAir_Dynamic")
    pizza_mesh = unrealsdk.find_object("StaticMesh", "Prop_Details.Meshes.PizzaBoxWhole")
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

def modify_southern_shelf(blg):
    flynt = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.Unique.PawnBalance_Flynt")
    setup_check_drop(blg, "Captain Flynt", flynt)

    boombewm = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Marauder.Balance.PawnBalance_BoomBoom")
    setup_check_drop(blg, "Boom Bewm", boombewm)

def modify_southern_shelf_bay(blg):
    midgemong = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_Warmong")
    setup_check_drop(blg, "Midgemong", midgemong)

def modify_frostburn(blg):
    scorch = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_SpiderAnt.Balance.Unique.PawnBalance_SpiderantScorch")
    setup_check_drop(blg, "Scorch", scorch)
    clayton = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_IncineratorVanya_Combat")
    setup_check_drop(blg, "Incinerator Clayton", clayton)
    spycho = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Spycho.Population.PawnBalance_Spycho")
    setup_check_drop(blg, "Spycho", spycho)

def modify_three_horns_divide(blg):
    savagelee = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_SavageLee")
    setup_check_drop(blg, "Savage Lee", savagelee)
    boll = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Z1_InMemoriamData.Balance.PawnBalance_Boll")
    setup_check_drop(blg, "Boll", boll)

def modify_three_horns_valley(blg):
    docmercy = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.Unique.PawnBalance_MrMercy")
    setup_check_drop(blg, "Doc Mercy", docmercy)

    badmaw = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.PawnBalance_BadMaw")
    setup_check_drop(blg, "Bad Maw", badmaw)

def modify_southpaw(blg):
    oney = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Marauder.Balance.Unique.PawnBalance_Assassin1")
    setup_check_drop(blg, "Assassin Oney", oney)
    wot = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.Unique.PawnBalance_Assassin2")
    setup_check_drop(blg, "Assassin Wot", wot)
    reeth = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_Assassin3")
    setup_check_drop(blg, "Assassin Reeth", reeth)
    rouf = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Assassin4")
    setup_check_drop(blg, "Assassin Rouf", rouf)

def modify_dust(blg):
    gettle = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Engineer.Balance.Unique.PawnBalance_Gettle")
    setup_check_drop(blg, "Gettle", gettle)
    mobley = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Marauder.Balance.Unique.PawnBalance_Mobley")
    setup_check_drop(blg, "Mobley", mobley)
    mcnally = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_McNally")
    setup_check_drop(blg, "McNally", mobley)
    blackqueen = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_SpiderAnt.Balance.Unique.PawnBalance_SpiderantBlackQueen")
    setup_check_drop(blg, "Black Queen", blackqueen)

    mick = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Marauder.Balance.Unique.PawnBalance_MickZaford_Combat")
    setup_check_drop(blg, "Mick/Tector", mick)
    tector = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Marauder.Balance.Unique.PawnBalance_TectorHodunk_Combat")
    setup_check_drop(blg, "Mick/Tector", tector)

def modify_bloodshot(blg):
    dan = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Dan")
    setup_check_drop(blg, "Dan", Dan)
    lee = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Lee")
    setup_check_drop(blg, "Lee", lee)
    mick = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Mick")
    setup_check_drop(blg, "Mick", mick)
    ralph = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Ralph")
    setup_check_drop(blg, "Ralph", ralph)
    flinter = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_RatEasterEgg")
    setup_check_drop(blg, "Flinter", flinter)
    madmike = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.Unique.PawnBalance_MadMike")
    setup_check_drop(blg, "Mad Mike", madmike)

def modify_bloodshot_ramparts(blg):
    w4rd3n = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Constructor.Balance.Unique.PawnBalance_ConstructorRoland")
    setup_check_drop(blg, "W4R-D3N", w4rd3n)

def modify_tundra_express(blg):
    bartlesby = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_BugMorph.Balance.Unique.PawnBalance_SirReginald")
    setup_check_drop(blg, "MadameVonBartlesby", bartlesby)

def modify_end_of_the_line(blg):
    wilhelm = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Loader.Balance.Unique.PawnBalance_Willhelm")
    setup_check_drop(blg, "Wilhelm", wilhelm)

def modify_fridge(blg):
    laney = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Laney")
    setup_check_drop(blg, "LaneyWhite", laney)
    rakkman = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_RakkMan")
    setup_check_drop(blg, "Rakkman", rakkman)
    smashhead = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Goliath.Balance.Unique.PawnBalance_SmashHead")
    setup_check_drop(blg, "SmashHead", smashhead)
    sinkhole = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Stalker.Balance.Unique.PawnBalance_Stalker_SwallowedWhole")
    setup_check_drop(blg, "Sinkhole", sinkhole)

def modify_highlands_outwash(blg):
    threshergluttonous = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Thresher.Balance.PawnBalance_ThresherGluttonous")
    setup_check_drop(blg, "GluttonousThresher", threshergluttonous)
    slappy = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Thresher.Balance.Unique.PawnBalance_Slappy")
    setup_check_drop(blg, "OldSlappy", slappy)

def modify_highlands(blg):
    henry = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Stalker.Balance.Unique.PawnBalance_Henry")
    setup_check_drop(blg, "Henry", henry)

def modify_caustic_caverns(blg):
    blue = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Crystalisk.Balance.Unique.PawnBalance_Blue")
    setup_check_drop(blg, "Blue", blue)
    creeperbadass = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Creeper.Balance.PawnBalance_CreeperBadass")
    setup_check_drop(blg, "BadassCreeper", creeperbadass)

def modify_wildlife_exploration_preserve(blg):
    tumbaa = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Skag.Balance.Unique.PawnBalance_Tumbaa")
    setup_check_drop(blg, "Tumbaa", tumbaa)
    stalker_simon = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Stalker.Balance.Unique.PawnBalance_Stalker_Simon")
    setup_check_drop(blg, "Pimon", stalker_simon)
    sonmothrakk = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rakk.Balance.Unique.PawnBalance_SonMothrakk")
    setup_check_drop(blg, "SonOfMothrakk", sonmothrakk)
    # Bloodwing will be weird

def modify_thousand_cuts(blg):
    # GOD-liath? it doesn't look like it has a separate loot pool GD_Population_Goliath.Balance.PawnBalance_GoliathBadass
    pass

def modify_lynchwood(blg):
    skagzilla = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Skag.Balance.Unique.PawnBalance_Skagzilla")
    setup_check_drop(blg, "DukinosMom", skagzilla)
    maddog = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_MadDog")
    setup_check_drop(blg, "MadDog", maddog)
    sheriff = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Sheriff.Balance.PawnBalance_Sheriff")
    setup_check_drop(blg, "SheriffNisha", sheriff)
    deputy = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Sheriff.Balance.PawnBalance_Deputy")
    setup_check_drop(blg, "DeputyWinger", deputy)

def modify_opportunity(blg):
    foreman = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Engineer.Balance.Unique.PawnBalance_Foreman")
    setup_check_drop(blg, "ForemanJasper", foreman)
    jacksbodydouble = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Jack.Balance.PawnBalance_JacksBodyDouble")
    setup_check_drop(blg, "JackBodyDouble", jacksbodydouble)

def modify_bunker(blg):
    # BNK-3R will be weird
    pass

def modify_eridium_blight(blg):
    kingmong = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_KingMong")
    setup_check_drop(blg, "KingMong", primalbeastkingmong_kingmong)

    donkeymong = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_DonkeyMong")
    setup_check_drop(blg, "DonkeyMong", donkeymong)

def modify_sawtooth_cauldron(blg):
    mortar = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Mortar")
    setup_check_drop(blg, "Mortar", mortar)

def modify_arid_nexus_boneyard(blg):
    djhyperion = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Engineer.Balance.Unique.PawnBalance_DJHyperion")
    setup_check_drop(blg, "HunterHellquist", djhyperion)

def modify_arid_nexus_badlands(blg):
    saturn = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Loader.Balance.Unique.PawnBalance_LoaderGiant")
    setup_check_drop(blg, "Saturn", saturn)
    bonehead2 = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Loader.Balance.Unique.PawnBalance_BoneHead2")
    setup_check_drop(blg, "BoneHead", bonehead2)

def modify_vault_of_the_warrior(blg):
    # Warrior will be weird
    pass

def modify_oasis(blg):
    pass

def modify_digi_peak(blg):
    pass

def modify_heros_pass(blg):
    pass


map_modifications = {
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
    "fridge_p": modify_fridge,
    "outwash_p": modify_highlands_outwash,
    "grass_p": modify_highlands,
    # "sanctuaryair_p": modify_sanctuary_air,
    "pandorapark_p": modify_wildlife_exploration_preserve,
    "grass_cliffs_p": modify_thousand_cuts,
    "hyperioncity_p": modify_opportunity,
    "ash_p": modify_eridium_blight,
    "craterlake_p": modify_sawtooth_cauldron,
    "fyrestone_p": modify_arid_nexus_boneyard,
    "stockade_p": modify_arid_nexus_badlands,
    "caverns_p": modify_caustic_caverns,
    "orchid_oasistown_p": modify_oasis,
    "testingzone_p": modify_digi_peak,
    "finalbossascent_p": modify_heros_pass,
    "tundraexpress_p": modify_tundra_express,
}