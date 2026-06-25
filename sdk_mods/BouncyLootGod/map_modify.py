from BouncyLootGod.state import get_globals, ApItemMesh
import unrealsdk
from ui_utils import show_chat_message
from mods_base import ENGINE, get_pc, Game
from BouncyLootGod.archi_data import loc_name_to_id
from BouncyLootGod.missions import move_sanctuary_blocked_missions, move_southern_shelf_blocked_missions
from BouncyLootGod.traps import is_trap_pawn_def
from BouncyLootGod.enemies import setup_check_drop, setup_generic_mob_drops
# orange = unrealsdk.make_struct("Color", R=128, G=64, B=0, A=255)



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


def modify_claptraps_place():
    # always enable so knuckle dragger's minions show up
    unrealsdk.find_object("PopulationOpportunityDen", "Glacial_Dynamic.TheWorld:PersistentLevel.PopulationOpportunityDen_0").isEnabled = True
    # spawn from the early monglet den if you're level 2+
    if get_pc().Pawn.GameStage >= 2:
        popmaster = unrealsdk.find_class("GearboxGlobals").ClassDefaultObject.GetGearboxGlobals().GetPopulationMaster()
        den = unrealsdk.find_object("PopulationOpportunityDen", "Glacial_Dynamic.TheWorld:PersistentLevel.PopulationOpportunityDen_15")
        for point in den.SpawnPoints:
            popdef = den.PopulationDef
            popfactory = popdef.ActorArchetypeList[0].SpawnFactory
            popfactory.SpawnAIPawn(
                Master=popmaster,
                SpawnLocationContextObject=None,
                SpawnLocation=point.Location,
                SpawnRotation=point.Rotation,
                GameStage=0, # popfactory.PawnBalanceDefinition.DefaultExpLevel
                AwesomeLevel=0
            )

def modify_southern_shelf():
    place_mesh_object(
        42273.96875, -28100.384765625, 660,
        "SouthernShelf_P.TheWorld:PersistentLevel.StaticMeshCollectionActor_100",
        "Prop_Barrels.Meshes.WoodenBarrel",
    )

def modify_southern_shelf_bay():
    pass

def modify_frostburn():
    place_mesh_object(
        -8715, 5683, -270,
        "icecanyon_p.TheWorld:PersistentLevel.StaticMeshCollectionActor_147",
        "Prop_Furniture.Chair",
        0, 5300, 0
    )

def modify_three_horns_divide():
    pass

def modify_three_horns_valley():
    pass

def modify_southpaw():
    pass

def modify_dust():
    # TODO change Black queen
    pass

def modify_bloodshot():
    pass

def modify_bloodshot_ramparts():
    bsi = unrealsdk.find_object("Behavior_SpawnItems", "GD_EasterEggs.InteractiveObjects.IO_MarcusSpawner:BehaviorProviderDefinition_0.Behavior_SpawnItems_156")
    setup_check_drop("Challenge BloodshotRamparts: Marcus Sacrifice", behavior_spawn_items=bsi)

def modify_tundra_express():
    pass

def modify_end_of_the_line():
    pass

def modify_fridge():
    pass

def modify_highlands_outwash():
    pass

def modify_highlands():
    pass

def modify_caustic_caverns():
    pass

def modify_wildlife_exploration_preserve():
    place_mesh_object(
        -14165, 29425, -2700,
        "PandoraPark_P.TheWorld:PersistentLevel.StaticMeshCollectionActor_165",
        "Prop_Railings.Mesh.Handrail128",
        6000, -15000, -15000
    )

def modify_thousand_cuts():
    pass

def modify_lynchwood():
    pass

def modify_opportunity():
    pass

def modify_bunker():
    pass

def modify_eridium_blight():
    pass

def modify_sawtooth_cauldron():
    pass

def modify_arid_nexus_boneyard():
    # into pipe
    place_mesh_object(
        -39794, 36853, -2043,
        "Fyrestone_P.TheWorld:PersistentLevel.StaticMeshCollectionActor_155",
        "Prop_Railings.Mesh.HyperionRailLong",
        6000, 2390, 0
    )

    # pipe up to ladder
    place_mesh_object(
        -28533, 31057, -1000,
        "Fyrestone_P.TheWorld:PersistentLevel.StaticMeshCollectionActor_155",
        "Prop_Railings.Mesh.HyperionRailLong",
        6500, -4090, 0
    )

def modify_arid_nexus_badlands():
    pass

def modify_vault_of_the_warrior():
    pass

def modify_sanctuary():
    unrealsdk.find_object("MissionDefinition", "GD_Z1_Assasinate.M_AssasinateTheAssassins").bRepeatable = True

def modify_sanctuary_air():
    unrealsdk.find_object("MissionDefinition", "GD_Z1_Assasinate.M_AssasinateTheAssassins").bRepeatable = True
    move_sanctuary_blocked_missions()

def modify_oasis():
    place_mesh_object(
        -30238, -5159, 7409,
        "Orchid_OasisTown_P.TheWorld:PersistentLevel.StaticMeshCollectionActor_99",
        "Prop_Furniture.Bench",
        0, 16000, 0
    )

    place_mesh_object(
        -30280, -5291, 7420,
        "Orchid_OasisTown_P.TheWorld:PersistentLevel.StaticMeshCollectionActor_99",
        "Prop_Bones.Meshes.SkagBone_06",
        # -16000, 0, -16000
        -7000, 0, 0
    )

def modify_digi_peak():
    pass

def modify_heros_pass():
    pass

def modify_gluttony_gulch():
    place_mesh_object(
        8814, -7851, -8235,
        "Hunger_P.TheWorld:PersistentLevel.StaticMeshCollectionActor_9",
        "Prop_Garbage.Meshes.CardboardBox",
        0, 0, 0
    )
    place_mesh_object(
        8717, -7803, -8250,
        "Hunger_P.TheWorld:PersistentLevel.StaticMeshCollectionActor_9",
        # "Prop_Garbage.Meshes.CardboardBox",
        "Prop_Garbage.Meshes.CardboardBoxes",
        0, 0, 20
    )

def modify_hunters_grotto():
    # edit Omnd-Omnd-Ohk chance
    aid = unrealsdk.find_object("AttributeInitializationDefinition", "GD_Native_Badass.WeightingPlayerCount.FireGod_PerPlayers")
    aid.ConditionalInitialization.ConditionalExpressionList = []
    aid.ConditionalInitialization.DefaultBaseValue.BaseValueConstant = 0.3

def modify_scyllas_grove():
    # edit Omnd-Omnd-Ohk chance
    aid = unrealsdk.find_object("AttributeInitializationDefinition", "GD_Native_Badass.WeightingPlayerCount.FireGod_PerPlayers")
    aid.ConditionalInitialization.ConditionalExpressionList = []
    aid.ConditionalInitialization.DefaultBaseValue.BaseValueConstant = 0.3

def modify_hayters_folly():
    place_mesh_object(
        -8283, -2775, -2838,
        "Orchid_Caves_P.TheWorld:PersistentLevel.StaticMeshCollectionActor_9",
        "Prop_Furniture.Chair",
        0, 0, 13000
    )

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
    "sanctuary_p": modify_sanctuary,
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
    "hunger_p": modify_gluttony_gulch,
    "sage_underground_p": modify_hunters_grotto,
    "sage_rockforest_p": modify_scyllas_grove,
    "orchid_caves_p": modify_hayters_folly,
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
