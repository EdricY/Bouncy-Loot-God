from mods_base import get_pc, Game
if Game.get_current().name == "TPS":
    from BouncyLootGod.bl_tps.traps import trap_pawn_def, init_game_traps, trigger_game_spawn_trap, trigger_game_trap
else:
    from BouncyLootGod.bl2.traps import trap_pawn_def, init_game_traps, trigger_game_spawn_trap, trigger_game_trap
    

def init_traps():
    init_game_traps()
def is_trap_pawn_def(pawn_def):
    return pawn_def.Name in trap_pawn_def


def trigger_trap(item_name, is_retry=False):
    if not item_name:
        return
    pieces = item_name.split(": ")
    if pieces[0] != "Trap":
        return
    trap_name = pieces[1]
    print("trigger_trap " + trap_name)
    try:
        trigger_game_trap(trap_name)
    except Exception as e:
        print("Failed to trigger trap " + trap_name + ", Reason + " + str(e))
        if not is_retry:
            init_traps()
            trigger_trap(item_name, True)
def trigger_spawn_trap(item_name, is_retry=False):
    if not item_name:
        return
    pieces = item_name.split(": ")
    if pieces[0] != "Trap Spawn":
        return
    spawn_name = pieces[1]
    print("trigger_spawn_trap " + spawn_name)
    try:
        trigger_game_spawn_trap(spawn_name)
    except Exception as e:
        print("Failed to Spawn " + spawn_name + ", Reason + " + str(e))
        if not is_retry:
            init_traps()
            trigger_spawn_trap(item_name, True)
        