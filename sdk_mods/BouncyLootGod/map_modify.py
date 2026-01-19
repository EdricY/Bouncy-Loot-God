import unrealsdk
from ui_utils import show_chat_message
from mods_base import ENGINE
from BouncyLootGod.archi_defs import loc_name_to_id

# orange = unrealsdk.make_struct("Color", R=128, G=64, B=0, A=255)


def create_pizza_item_pool(blg, check_name):
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
    # try:
    #     pizza_mesh = unrealsdk.find_object("StaticMesh", "Prop_Details.Meshes.PizzaBoxWhole")
    # except:
    #     unrealsdk.load_package("SanctuaryAir_Dynamic")
    #     pizza_mesh = unrealsdk.find_object("StaticMesh", "Prop_Details.Meshes.PizzaBoxWhole")
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
    return item_pool

def setup_check_drop(blg, check_name, ai_pawn_bd=None, behavior_spawn_items=None, chance=1.0):
    if not ai_pawn_bd and not behavior_spawn_items:
        print("don't know where to put check: " + check_name)
        return

    item_pool = create_pizza_item_pool(blg, check_name)
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
    if ai_pawn_bd:
        if len(ai_pawn_bd.DefaultItemPoolList) > 0:
            ai_pawn_bd.DefaultItemPoolList.append(item_pool_info)
        else:
            for pt in ai_pawn_bd.PlayThroughs:
                pt.CustomItemPoolList.append(item_pool_info)

    elif behavior_spawn_items:
        behavior_spawn_items.ItemPoolList.append(item_pool_info)

def place_mesh_object(
    x, y, z,
    static_mesh_collection_actor_name, static_mesh_name="Prop_Details.Meshes.PizzaBoxWhole",
    pitch=0, yaw=0, roll=0
):
    try:
        mesh = unrealsdk.find_object("StaticMesh", static_mesh_name)
    except:
        unrealsdk.load_package("SanctuaryAir_Dynamic")
        mesh = unrealsdk.find_object("StaticMesh", static_mesh_name)

    smc = ENGINE.GetCurrentWorldInfo().MyEmitterPool.GetFreeStaticMeshComponent(True)
    smc.SetStaticMesh(mesh, True)
    smc.SetBlockRigidBody(True)
    smc.SetActorCollision(True, True, True)
    smc.SetTraceBlocking(True, True)

    ca = unrealsdk.find_object("StaticMeshCollectionActor", static_mesh_collection_actor_name)
    ca.AttachComponent(smc)

    smc.CachedParentToWorld.WPlane.X = x
    smc.CachedParentToWorld.WPlane.Y = y
    smc.CachedParentToWorld.WPlane.Z = z
    smc.Rotation = unrealsdk.make_struct("Rotator", Pitch=pitch, Yaw=yaw, Roll=roll)
    smc.ForceUpdate(False)
    smc.SetComponentRBFixed(True)


def modify_claptraps_place(blg):
    # knuck = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_KnuckleDragger")
    # setup_check_drop(blg, "Knuckle Dragger", knuck)
    pass

def modify_southern_shelf(blg):
    place_mesh_object(
        42273.96875, -28100.384765625, 660,
        "SouthernShelf_P.TheWorld:PersistentLevel.StaticMeshCollectionActor_100",
        "Prop_Barrels.Meshes.WoodenBarrel",
    )

    # flynt = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.Unique.PawnBalance_Flynt")
    # setup_check_drop(blg, "Captain Flynt", flynt)

    # boombewm = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Marauder.Balance.PawnBalance_BoomBoom")
    # setup_check_drop(blg, "Boom Bewm", boombewm)

def modify_southern_shelf_bay(blg):
    # midgemong = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_Warmong")
    # setup_check_drop(blg, "Midgemong", midgemong)
    pass

def modify_frostburn(blg):
    place_mesh_object(
        -8715, 5683, -270,
        "icecanyon_p.TheWorld:PersistentLevel.StaticMeshCollectionActor_147",
        "Prop_Furniture.Chair",
        0, 5300, 0
    )

    # scorch = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_SpiderAnt.Balance.Unique.PawnBalance_SpiderantScorch")
    # setup_check_drop(blg, "Scorch", scorch)
    # clayton = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_IncineratorVanya_Combat")
    # setup_check_drop(blg, "Incinerator Clayton", clayton)
    # spycho = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Spycho.Population.PawnBalance_Spycho")
    # setup_check_drop(blg, "Spycho", spycho)
    pass

def modify_three_horns_divide(blg):
    # savagelee = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_SavageLee")
    # setup_check_drop(blg, "Savage Lee", savagelee)
    # boll = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Z1_InMemoriamData.Balance.PawnBalance_Boll")
    # setup_check_drop(blg, "Boll", boll)
    pass

def modify_three_horns_valley(blg):
    pass

    # docmercy = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.Unique.PawnBalance_MrMercy")
    # setup_check_drop(blg, "Doc Mercy", docmercy)

    # badmaw = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.PawnBalance_BadMaw")
    # setup_check_drop(blg, "Bad Maw", badmaw)
    
    # badmaw = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.PawnBalance_BadMaw")
    # setup_check_drop(blg, "Bad Maw", badmaw)


def modify_southpaw(blg):
    # oney = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.Unique.PawnBalance_Assassin2")
    # setup_check_drop(blg, "Assassin Oney", oney)
    # wot = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Marauder.Balance.Unique.PawnBalance_Assassin1")
    # setup_check_drop(blg, "Assassin Wot", wot)
    # reeth = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_Assassin3")
    # setup_check_drop(blg, "Assassin Reeth", reeth)
    # rouf = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Assassin4")
    # setup_check_drop(blg, "Assassin Rouf", rouf)
    pass

def modify_dust(blg):
    # gettle = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Engineer.Balance.Unique.PawnBalance_Gettle")
    # setup_check_drop(blg, "Gettle", gettle)
    # mobley = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Marauder.Balance.Unique.PawnBalance_Mobley")
    # setup_check_drop(blg, "Mobley", mobley)
    # mcnally = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_McNally")
    # setup_check_drop(blg, "McNally", mobley)
    # blackqueen = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_SpiderAnt.Balance.Unique.PawnBalance_SpiderantBlackQueen")
    # setup_check_drop(blg, "Black Queen", blackqueen)

    # mick = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Marauder.Balance.Unique.PawnBalance_MickZaford_Combat")
    # setup_check_drop(blg, "Mick/Tector", mick)
    # tector = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Marauder.Balance.Unique.PawnBalance_TectorHodunk_Combat")
    # setup_check_drop(blg, "Mick/Tector", tector)
    pass

def modify_bloodshot(blg):
    # dan = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Dan")
    # setup_check_drop(blg, "Dan", dan)
    # lee = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Lee")
    # setup_check_drop(blg, "Lee", lee)
    # mick = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Mick")
    # setup_check_drop(blg, "Mick", mick)
    # ralph = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Ralph")
    # setup_check_drop(blg, "Ralph", ralph)
    # flinter = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_RatEasterEgg")
    # setup_check_drop(blg, "Flinter", flinter)
    # madmike = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Nomad.Balance.Unique.PawnBalance_MadMike")
    # setup_check_drop(blg, "Mad Mike", madmike)
    pass

def modify_bloodshot_ramparts(blg):
    print("modify_bloodshot_ramparts")
    if loc_name_to_id["Challenge BloodshotRamparts: Marcus Sacrifice"] not in blg.locations_checked:
        bsi = unrealsdk.find_object("Behavior_SpawnItems", "GD_EasterEggs.InteractiveObjects.IO_MarcusSpawner:BehaviorProviderDefinition_0.Behavior_SpawnItems_156")
        setup_check_drop(blg, "Challenge BloodshotRamparts: Marcus Sacrifice", behavior_spawn_items=bsi)

    # ipld = unrealsdk.construct_object("ItemPoolListDefinition", blg.package, "archi_marcus_pool_list", 0)
    # prob = unrealsdk.make_struct(
    #     "AttributeInitializationData",
    #     BaseValueConstant=1.0,
    #     BaseValueAttribute=None,
    #     InitializationDefinition=None,
    #     BaseValueScaleConstant=1.000000
    # )
    # item_pool_info = unrealsdk.make_struct(
    #     "ItemPoolInfo",
    #     ItemPool=create_pizza_item_pool(blg, "Marcus Sacrifice"),
    #     PoolProbability=prob
    # )
    # ipld.ItemPools = [item_pool_info]
    # bsi.ItemPoolIncludedLists[0] = ipld

    # GD_EasterEggs.InteractiveObjects.IO_MarcusSpawner:BehaviorProviderDefinition_0.Behavior_SpawnItems_156
    # w4rd3n = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Constructor.Balance.Unique.PawnBalance_ConstructorRoland")
    # setup_check_drop(blg, "W4R-D3N", w4rd3n)

def modify_tundra_express(blg):
    # bartlesby = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_BugMorph.Balance.Unique.PawnBalance_SirReginald")
    # setup_check_drop(blg, "Madame Von Bartlesby", bartlesby)
    pass

def modify_end_of_the_line(blg):
    # wilhelm = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Loader.Balance.Unique.PawnBalance_Willhelm")
    # setup_check_drop(blg, "Wilhelm", wilhelm)
    pass

def modify_fridge(blg):
    # laney = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Laney")
    # setup_check_drop(blg, "Laney White", laney)
    # rakkman = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_RakkMan")
    # setup_check_drop(blg, "Rakkman", rakkman)
    # smashhead = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Goliath.Balance.Unique.PawnBalance_SmashHead")
    # setup_check_drop(blg, "SmashHead", smashhead)
    # sinkhole = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Stalker.Balance.Unique.PawnBalance_Stalker_SwallowedWhole")
    # setup_check_drop(blg, "Sinkhole", sinkhole)
    pass

def modify_highlands_outwash(blg):
    # threshergluttonous = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Thresher.Balance.PawnBalance_ThresherGluttonous")
    # setup_check_drop(blg, "Gluttonous Thresher", threshergluttonous)
    # slappy = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Thresher.Balance.Unique.PawnBalance_Slappy")
    # setup_check_drop(blg, "Old Slappy", slappy)
    pass

def modify_highlands(blg):
    # henry = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Stalker.Balance.Unique.PawnBalance_Henry")
    # setup_check_drop(blg, "Henry", henry)
    pass

def modify_caustic_caverns(blg):
    # blue = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Crystalisk.Balance.Unique.PawnBalance_Blue")
    # setup_check_drop(blg, "Blue", blue)
    # creeperbadass = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Creeper.Balance.PawnBalance_CreeperBadass")
    # setup_check_drop(blg, "BadassCreeper", creeperbadass)
    pass

def modify_wildlife_exploration_preserve(blg):
    place_mesh_object(
        -14165, 29425, -2700,
        "PandoraPark_P.TheWorld:PersistentLevel.StaticMeshCollectionActor_165",
        "Prop_Railings.Mesh.Handrail128",
        6000, -15000, -15000
    )

    # tumbaa = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Skag.Balance.Unique.PawnBalance_Tumbaa")
    # setup_check_drop(blg, "Tumbaa", tumbaa)
    # pimon = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Stalker.Balance.Unique.PawnBalance_Stalker_Simon")
    # setup_check_drop(blg, "Pimon", pimon)
    # sonmothrakk = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rakk.Balance.Unique.PawnBalance_SonMothrakk")
    # setup_check_drop(blg, "Son of Mothrakk", sonmothrakk)
    # Bloodwing will be weird
    pass

def modify_thousand_cuts(blg):
    # GOD-liath? it doesn't look like it has a separate loot pool GD_Population_Goliath.Balance.PawnBalance_GoliathBadass
    pass

def modify_lynchwood(blg):
    # skagzilla = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Skag.Balance.Unique.PawnBalance_Skagzilla")
    # setup_check_drop(blg, "Dukino's Mom", skagzilla)
    # maddog = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Psycho.Balance.Unique.PawnBalance_MadDog")
    # setup_check_drop(blg, "Mad Dog", maddog)
    # sheriff = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Sheriff.Balance.PawnBalance_Sheriff")
    # setup_check_drop(blg, "Sheriff Nisha", sheriff)
    # deputy = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Sheriff.Balance.PawnBalance_Deputy")
    # setup_check_drop(blg, "Deputy VaultOfTheWarriorWinger", deputy)
    pass

def modify_opportunity(blg):
    # foreman = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Engineer.Balance.Unique.PawnBalance_Foreman")
    # setup_check_drop(blg, "Foreman Jasper", foreman)
    # jacksbodydouble = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Jack.Balance.PawnBalance_JacksBodyDouble")
    # setup_check_drop(blg, "Jack's Body Double", jacksbodydouble)
    pass

def modify_bunker(blg):
    if loc_name_to_id["Enemy: BNK-3R"] not in blg.locations_checked:
        setup_check_drop(blg, "Enemy: BNK-3R", behavior_spawn_items=unrealsdk.find_object("Behavior_SpawnItems", "GD_HyperionBunkerBoss.Character.AIDef_BunkerBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_0"))

def modify_eridium_blight(blg):
    # kingmong = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_KingMong")

    # setup_check_drop(blg, "King Mong", kingmong)
    # donkeymong = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_PrimalBeast.Balance.Unique.PawnBalance_PrimalBeast_DonkeyMong")
    # setup_check_drop(blg, "Donkey Mong", donkeymong)
    pass

def modify_sawtooth_cauldron(blg):
    # mortar = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Rat.Balance.Unique.PawnBalance_Mortar")
    # setup_check_drop(blg, "Mortar", mortar)
    pass

def modify_arid_nexus_boneyard(blg):
    # djhyperion = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Engineer.Balance.Unique.PawnBalance_DJHyperion")
    # setup_check_drop(blg, "Hunter Hellquist", djhyperion)
    pass

def modify_arid_nexus_badlands(blg):
    # saturn = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Loader.Balance.Unique.PawnBalance_LoaderGiant")
    # setup_check_drop(blg, "Saturn", saturn)
    # bonehead2 = unrealsdk.find_object("AIPawnBalanceDefinition", "GD_Population_Loader.Balance.Unique.PawnBalance_BoneHead2")
    # setup_check_drop(blg, "Bone Head 2.0", bonehead2)
    pass

def modify_vault_of_the_warrior(blg):
    if loc_name_to_id["Enemy: Warrior"] not in blg.locations_checked:
        setup_check_drop(blg, "Enemy: Warrior", behavior_spawn_items=unrealsdk.find_object("Behavior_SpawnItems", "Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_31.Behavior_SpawnItems_6"))
    # setup_check_drop(blg, "Enemy: Warrior", behavior_spawn_items=unrealsdk.find_object("Behavior_SpawnItems", "GD_FinalBoss.Character.AIDef_FinalBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_17"))
    # setup_check_drop(blg, "Enemy: Warrior 1",behavior_spawn_items=unrealsdk.find_object("Behavior_SpawnItems", "Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_16.Behavior_SpawnItems_6"))
    # setup_check_drop(blg, "Enemy: Warrior 3",behavior_spawn_items=unrealsdk.find_object("Behavior_SpawnItems", "Boss_Volcano_Combat_Monster.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_59.Behavior_SpawnItems_6"))
    # setup_check_drop(blg, "Enemy: Warrior 5", behavior_spawn_items=unrealsdk.find_object("Behavior_SpawnItems", "GD_FinalBoss.Character.AIDef_FinalBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_16"))
    # setup_check_drop(blg, "Enemy: Warrior 6", behavior_spawn_items=unrealsdk.find_object("Behavior_SpawnItems", "GD_FinalBoss.Character.AIDef_FinalBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_15"))
    # setup_check_drop(blg, "Enemy: Warrior 7", behavior_spawn_items=unrealsdk.find_object("Behavior_SpawnItems", "GD_FinalBoss.Character.AIDef_FinalBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_14"))
    # setup_check_drop(blg, "Enemy: Warrior 8", behavior_spawn_items=unrealsdk.find_object("Behavior_SpawnItems", "GD_FinalBoss.Character.AIDef_FinalBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_13"))
    # setup_check_drop(blg, "Enemy: Warrior 9", behavior_spawn_items=unrealsdk.find_object("Behavior_SpawnItems", "GD_FinalBoss.Character.AIDef_FinalBoss:AIBehaviorProviderDefinition_1.Behavior_SpawnItems_12"))


def modify_sanctuary_air(blg):
    pass

def modify_oasis(blg):
    pass

def modify_digi_peak(blg):
    pass

def modify_heros_pass(blg):
    pass


def setup_generic_mob_drops(blg):
    if blg.settings.get("generic_mob_checks", 0) == 0:
        return

    all_pawns = unrealsdk.find_all("AIPawnBalanceDefinition")
    # print([str(pawn).lower() for pawn in all_pawns])

    chance = blg.settings.get("generic_mob_checks", 5) * 0.01

    if loc_name_to_id["Generic: Skag"] not in blg.locations_checked:
        for pawn in [pawn for pawn in all_pawns if "skag" in str(pawn).lower()]:
            setup_check_drop(blg, "Generic: Skag", pawn, chance=chance)

    if loc_name_to_id["Generic: Rakk"] not in blg.locations_checked:
        for pawn in [pawn for pawn in all_pawns if "rakk" in str(pawn).lower()]:
            setup_check_drop(blg, "Generic: Rakk", pawn, chance=chance)

    if loc_name_to_id["Generic: Bullymong"] not in blg.locations_checked:
        for pawn in [pawn for pawn in all_pawns if "primalbeast" in str(pawn).lower()]:
            setup_check_drop(blg, "Generic: Bullymong", pawn, chance=chance)

    if loc_name_to_id["Generic: Psycho"] not in blg.locations_checked:
        for pawn in [pawn for pawn in all_pawns if "psycho" in str(pawn).lower()]:
            setup_check_drop(blg, "Generic: Psycho", pawn, chance=chance)

    if loc_name_to_id["Generic: Rat"] not in blg.locations_checked:
        for pawn in [pawn for pawn in all_pawns if "_rat" in str(pawn).lower()]:
            setup_check_drop(blg, "Generic: Rat", pawn, chance=chance)

    if loc_name_to_id["Generic: Spiderant"] not in blg.locations_checked:
        for pawn in [pawn for pawn in all_pawns if "spiderant" in str(pawn).lower()]:
            setup_check_drop(blg, "Generic: Spiderant", pawn, chance=chance)

    if loc_name_to_id["Generic: Varkid"] not in blg.locations_checked:
        for pawn in [pawn for pawn in all_pawns if "bugmorph" in str(pawn).lower()]:
            setup_check_drop(blg, "Generic: Varkid", pawn, chance=chance)

    if loc_name_to_id["Generic: Goliath"] not in blg.locations_checked:
        for pawn in [pawn for pawn in all_pawns if "goliath" in str(pawn).lower()]:
            setup_check_drop(blg, "Generic: Goliath", pawn, chance=chance)

    if loc_name_to_id["Generic: Marauder"] not in blg.locations_checked:
        for pawn in [pawn for pawn in all_pawns if "marauder" in str(pawn).lower()]:
            setup_check_drop(blg, "Generic: Marauder", pawn, chance=chance)

    if loc_name_to_id["Generic: Stalker"] not in blg.locations_checked:
        for pawn in [pawn for pawn in all_pawns if "stalker" in str(pawn).lower()]:
            setup_check_drop(blg, "Generic: Stalker", pawn, chance=chance)

    if loc_name_to_id["Generic: Midget"] not in blg.locations_checked:
        for pawn in [pawn for pawn in all_pawns if "midget" in str(pawn).lower()]:
            setup_check_drop(blg, "Generic: Midget", pawn, chance=chance)

    if loc_name_to_id["Generic: Nomad"] not in blg.locations_checked:
        for pawn in [pawn for pawn in all_pawns if "nomad" in str(pawn).lower()]:
            setup_check_drop(blg, "Generic: Nomad", pawn, chance=chance)

    if loc_name_to_id["Generic: Thresher"] not in blg.locations_checked:
        for pawn in [pawn for pawn in all_pawns if "thresher" in str(pawn).lower() and "tentacle" not in str(pawn).lower()]:
            setup_check_drop(blg, "Generic: Thresher", pawn, chance=chance)

    if loc_name_to_id["Generic: Badass"] not in blg.locations_checked:
        for pawn in [pawn for pawn in all_pawns if "badass" in str(pawn).lower()]:
            setup_check_drop(blg, "Generic: Badass", pawn, chance=chance)



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
    "grass_lynchwood_p": modify_lynchwood,
    "sanctuaryair_p": modify_sanctuary_air,
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
    "boss_cliffs_p": modify_bunker,
    "boss_volcano_p": modify_vault_of_the_warrior,
}


map_area_to_name = {
    "fyrestone_p":              "Arid Nexus Boneyard",
    "luckys_p":                 "The Holy Spirits",
    "southpawfactory_p":        "Southpaw Steam & Power",
    "sanctuary_hole_p":         "Sanctuary Hole",
    "finalbossascent_p":        "Hero's Pass",
    "dam_p":                    "Bloodshot Stronghold",
    "frost_p":                  "Three Horns Valley",
    "sanctuary_p":              "Sanctuary",
    "sanctuaryair_p":           "Sanctuary",
    "grass_cliffs_p":           "Thousand Cuts",
    "tundratrain_p":            "End of the Line",
    "pandorapark_p":            "Wildlife Exploitation Preserve",
    "thresherraid_p":           "Terramorphous Peak",
    "tundraexpress_p":          "Tundra Express",
    "fridge_p":                 "The Fridge",
    "banditslaughter_p":        "Fink's Slaughterhouse",
    "cove_p":                   "Southern Shelf Bay",
    "icecanyon_p":              "Frostburn Canyon",
    "ice_p":                    "Three Horns Divide",
    "grass_p":                  "Highlands",
    "creatureslaughter_p":      "Natural Selection Annex",
    "interlude_p":              "The Dust",
    "hypinterlude_p":           "Friendship Gulag",
    "hyperioncity_p":           "Opportunity",
    "damtop_p":                 "Bloodshot Ramparts",
    "stockade_p":               "Arid Nexus Badlands",
    "southernshelf_p":          "Southern Shelf",
    "outwash_p":                "Highlands Outwash",
    "caverns_p":                "Caustic Caverns",
    "grass_lynchwood_p":        "Lynchwood",
    "glacial_p":                "Windshear Waste",
    "craterlake_p":             "Sawtooth Cauldron",
    "robotslaughter_p":         "Ore Chasm",
    "boss_cliffs_p":            "The Bunker",
    "vogchamber_p":             "Control Core Angel",
    "boss_volcano_p":           "Vault of the Warrior",
    "ash_p":                    "Eridium Blight",
    "hunger_p":                 "Gluttony Gulch",
    "xmas_p":                   "Marcus's Mercenary Shop",
    "helios_p":                 "Helios Fallen",
    "gaiussanctuary_p":         "FFS Boss Fight",
    "backburner_p":             "The Backburner",
    "sanctintro_p":             "FFS Intro Sanctuary",
    "olddust_p":                "Dahl Abandon",
    "researchcenter_p":         "Mt. Scarab Research Center",
    "sandworm_p":               "The Burrows",
    "sandwormlair_p":           "Writhing Deep",
    "dark_forest_p":            "The Forest",
    "dead_forest_p":            "Immortal Woods",
    "castlekeep_p":             "Dragon Keep",
    "docks_p":                  "Unassuming Docks",
    "village_p":                "Flamerock Refuge",
    "castleexterior_p":         "Hatred's Shadow",
    "dungeon_p":                "Lair of Infinite Agony",
    "templeslaughter_p":        "Murderlin's Temple",
    "mines_p":                  "Mines of Avarice",
    "dungeonraid_p":            "The Winged Storm",
    "pumpkin_patch_p":          "Hallowed Hollow",
    "iris_dl1_p":               "Torgue Arena",
    "iris_dl1_tas_p":           "Torgue Arena",
    "iris_dl2_p":               "The Beatdown",
    "iris_dl3_p":               "The Forge",
    "iris_hub_p":               "Badass Crater",
    "iris_hub2_p":              "Southern Raceway",
    "iris_dl2_interior_p":      "Pyro Pete's Bar",
    "iris_moxxi_p":             "Badass Crater Bar",
    "testingzone_p":            "Digistruct Peak",
    "easter_p":                 "Wam Bam Island",
    "distillery_p":             "Rotgut Distillery",
    "orchid_wormbelly_p":       "The Leviathan's Lair",
    "orchid_refinery_p":        "Washburne Refinery",
    "orchid_saltflats_p":       "Wurmwater",
    "orchid_spire_p":           "Magnys Lighthouse",
    "orchid_shipgraveyard_p":   "The Rustyards",
    "orchid_caves_p":           "Hayter's Folly",
    "orchid_oasistown_p":       "Oasis",
    "sage_powerstation_p":      "Ardorton Station",
    "sage_underground_p":       "Hunter's Grotto",
    "sage_cliffs_p":            "Candlerakk's Cragg",
    "sage_hyperionship_p":      "Terminus",
    "sage_rockforest_p":        "Scylla's Grove",
}
