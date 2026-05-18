from BouncyLootGod.oob import get_loc_in_front_of_player
import unrealsdk
from mods_base import get_pc, Game
if Game.get_current().name == "TPS":
    from BouncyLootGod.bl_tps.traps import trap_pawn_def, init_game_traps, get_game_spawn_trap, trigger_game_trap
else:
    from BouncyLootGod.bl2.traps import trap_pawn_def, init_game_traps, get_game_spawn_trap, trigger_game_trap
    

def init_traps(): #TODO add game separation
    init_game_traps()
def is_trap_pawn_def(pawn_def):
    return pawn_def.Name in trap_pawn_def

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



def trigger_trap(item_name, is_retry=False):
    if not item_name:
        return
    pieces = item_name.split(": ")
    if pieces[0] != "Trap":
        return
    trap_name = pieces[1]
    print("trigger_trap " + trap_name)
    try:
        if trigger_game_trap(trap_name):
            return #the game handled the trap
        elif trap_name == "Slippery": #just drop current weapon
            pc = get_pc()
            pc.ServerThrowPawnActiveWeapon()
        elif trap_name == "Item Explosion": #throw all items in backpack.
            pc = get_pc()
            im = pc.GetPawnInventoryManager()
            backpack = im.Backpack[:]
            for item in backpack:
                pc.ServerThrowInventory(item, 1)
            im.Backpack = []
            #this is needed as the game does not update the internal counter, 
            # leading to "full backpack" error with available slots when trying to pick up items
            im.ServerUpdateBackpackInventoryCount(0)

    except Exception as e:
        print("Failed to trigger trap " + trap_name + ", Reason + " + str(e))
        if not is_retry:
            init_game_traps()
            trigger_trap(item_name, True)
def trigger_spawn_trap(item_name, is_retry=False):
    if not item_name:
        return
    pieces = item_name.split(": ")
    if pieces[0] != "Trap Spawn":
        return
    spawn_name = pieces[1]
    print("trigger_spawn_trap " + spawn_name)
    spawns = get_game_spawn_trap(spawn_name, False)
    if not spawns:
        print("Failed to Spawn " + spawn_name + ", Reason + " + "game spawn returned None")
    try:
        for spawn in spawns:
            dists = getattr(spawn, "dists", None)
            popfactory = unrealsdk.find_object("PopulationFactoryBalancedAIPawn", spawn.ai_pawn)
            relative_pos = getattr(spawn, "relative_pos", None)
            if dists:
                for dist in dists:
                    spawn_at_dist(popfactory, dist)
            elif relative_pos:
                for pos in relative_pos:
                    spawn_at_relative(popfactory, x= getattr(pos, "x", 0), y=getattr(pos, "y", 0))
    except Exception as e:
        print("Failed to Spawn " + spawn_name + ", Reason + " + str(e))
        if not is_retry:
            init_traps()
            trigger_spawn_trap(item_name, True)
        