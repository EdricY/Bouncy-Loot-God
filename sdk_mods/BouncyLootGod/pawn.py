import unrealsdk
from mods_base import get_pc, Game
from BouncyLootGod.oob import get_loc_in_front_of_player

def spawn_at_dist(popfactory, dist=1000, height=0):
    pc = get_pc()
    popmaster = unrealsdk.find_class("GearboxGlobals").ClassDefaultObject.GetGearboxGlobals().GetPopulationMaster()
    popmaster.SpawnActorFromOpportunity(
        SpawnLocation=get_loc_in_front_of_player(dist=dist, height=height),
        TheFactory=popfactory,
        SpawnLocationContextObject=None,
        SpawnRotation=unrealsdk.make_struct("Rotator", Pitch=0, Yaw=0, Roll=0),
        GameStage=pc.PlayerReplicationInfo.ExpLevel,
        Rarity=1,
        OpportunityIdx=0,
        PopOppFlags=0,
    )

    # popfactory.SpawnAIPawn(
    #     Master=popmaster,
    #     SpawnLocationContextObject=None,
    #     SpawnLocation=get_loc_in_front_of_player(dist=dist, height=height),
    #     SpawnRotation=unrealsdk.make_struct("Rotator", Pitch=0, Yaw=0, Roll=0),
    #     GameStage=10,
    #     AwesomeLevel=0
    # )


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
