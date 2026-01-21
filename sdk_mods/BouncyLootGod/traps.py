from BouncyLootGod.oob import get_loc_in_front_of_player
import unrealsdk
from mods_base import get_pc


def spawn_at_dist(popfactory, dist=1000):
    pc = get_pc()
    popmaster = unrealsdk.find_class("GearboxGlobals").ClassDefaultObject.GetGearboxGlobals().GetPopulationMaster()
    popmaster.SpawnActorFromOpportunity(
        SpawnLocation=get_loc_in_front_of_player(dist=1000, height=0),
        TheFactory=popfactory,
        SpawnLocationContextObject=None,
        SpawnRotation=unrealsdk.make_struct("Rotator", Pitch=0, Yaw=0, Roll=0),
        GameStage=pc.PlayerReplicationInfo.ExpLevel,
        Rarity=1,
        OpportunityIdx=0,
        PopOppFlags=0,
    )

def spawn_at_relative(popfactory, x=0, y=0, z=0):
    pc = get_pc()
    pawn = pc.Pawn
    rel_loc = unrealsdk.make_struct(
        "Vector", 
        X=pawn.Location.X + x,
        Y=pawn.Location.Y + y,
        Z=pawn.Location.Z + z,
    )
    popmaster = unrealsdk.find_class("GearboxGlobals").ClassDefaultObject.GetGearboxGlobals().GetPopulationMaster()
    popmaster.SpawnActorFromOpportunity(
        SpawnLocation=rel_loc,
        TheFactory=popfactory,
        SpawnLocationContextObject=None,
        SpawnRotation=unrealsdk.make_struct("Rotator", Pitch=0, Yaw=0, Roll=0),
        GameStage=pc.PlayerReplicationInfo.ExpLevel,
        Rarity=1,
        OpportunityIdx=0,
        PopOppFlags=0,
    )



def trigger_spawn_trap(item_name):
    if not item_name:
        return
    pieces = item_name.split(": ")
    if pieces[0] != "Trap Spawn":
        return
    spawn_name = pieces[1]
    print("trigger_spawn_trap " + spawn_name)

    if spawn_name == "Black Queen":
        unrealsdk.load_package("TESTINGZONE_COMBAT")
        popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_SpiderantBlackQueen_Digi.Population.PopDef_SpiderantBlackQueen_Digi:PopulationFactoryBalancedAIPawn_0")
        spawn_at_dist(popfactory, dist=1000)
        spawn_at_dist(popfactory, dist=-1000)
    elif spawn_name == "Saturn":
        unrealsdk.load_package("TESTINGZONE_COMBAT")
        popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_LoaderUltimateBadass_Digi.Population.PopDef_LoaderUltimateBadass_Digi:PopulationFactoryBalancedAIPawn_1")
        spawn_at_dist(popfactory, dist=1000)
        spawn_at_dist(popfactory, dist=-1000)
    elif spawn_name == "Doc Mercy":
        unrealsdk.load_package("TESTINGZONE_COMBAT")
        popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_MrMercy_Digi.Population.PopDef_MrMercy_Digi:PopulationFactoryBalancedAIPawn_0")
        spawn_at_dist(popfactory, dist=1000)
        spawn_at_dist(popfactory, dist=-1000)
    elif spawn_name == "Dukino's Mom":
        unrealsdk.load_package("TESTINGZONE_COMBAT")
        popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Skagzilla_Digi.Population.PopDef_Skagzlla_Digi:PopulationFactoryBalancedAIPawn_1")
        spawn_at_dist(popfactory, dist=1000)
        spawn_at_dist(popfactory, dist=-1000)
    elif spawn_name == "Creepers":
        unrealsdk.load_package("caverns_p")
        popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Population_Creeper.Population.PopDef_CreeperMix_Regular:PopulationFactoryBalancedAIPawn_0")
        spawn_at_relative(popfactory, x=1000)
        spawn_at_relative(popfactory, x=-1000)
        spawn_at_relative(popfactory, y=1000)
        spawn_at_relative(popfactory, y=-1000)
        spawn_at_relative(popfactory, x=1000, y=1000)
        spawn_at_relative(popfactory, x=-1000, y=1000)
        spawn_at_relative(popfactory, x=1000, y=-1000)
        spawn_at_relative(popfactory, x=-1000, y=-1000)
    elif spawn_name == "Assassins":
        unrealsdk.load_package("TESTINGZONE_COMBAT")
        popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Assassin1_Digi.Population.PopDef_Assassin1_Digi:PopulationFactoryBalancedAIPawn_0")
        spawn_at_relative(popfactory, x=1000)
        popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Assassin2_Digi.Population.PopDef_Assassin2_Digi:PopulationFactoryBalancedAIPawn_0")
        spawn_at_relative(popfactory, x=-1000)
        popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Assassin3_Digi.Population.PopDef_Assassin3_Digi:PopulationFactoryBalancedAIPawn_0")
        spawn_at_relative(popfactory, y=1000)
        popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Assassin4_Digi.Population.PopDef_Assassin4_Digi:PopulationFactoryBalancedAIPawn_0")
        spawn_at_relative(popfactory, y=-1000)


    # unrealsdk.load_package("tundraexpress_p")
    # popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Population_BugMorph.Population.PopDef_BugMorphRaid:PopulationFactoryBalancedAIPawn_0")

    # unrealsdk.load_package("TundraExpress_Dynamic")
    # popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Population_BugMorph.Population.Unique.PopDef_SirReginald:PopulationFactoryBalancedAIPawn_1")
    
    # unrealsdk.load_package("TundraExpress_Combat")
    # popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Population_BugMorph.Population.PopDef_BugMorphUltimateBadass:PopulationFactoryBalancedAIPawn_1")

    # unrealsdk.load_package("TESTINGZONE_COMBAT")
    # popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_MarauderBadass_Digi.Population.PopDef_MarauderBadass_Digi:PopulationFactoryBalancedAIPawn_0")
