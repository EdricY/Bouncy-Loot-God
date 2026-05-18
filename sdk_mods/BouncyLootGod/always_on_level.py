import unrealsdk.unreal as unreal
from mods_base import build_mod, get_pc, hook, SpinnerOption, BoolOption
from unrealsdk.hooks import Block, prevent_hooking_direct_calls
from BouncyLootGod.state import get_globals


@hook("WillowGame.WillowPawn:SetGameStage")
@hook("WillowGame.WillowInteractiveObject:SetGameStage")
@hook("WillowGame.WillowPawn:SetGameStageForSpawnedInventory")
@hook("WillowGame.WillowAIPawn:SetGameStageForSpawnedInventory")
def set_always_on_level(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
  blg = get_globals()
  setting = blg.settings.get("always_on_level", 0)
  if setting == 0:
    return None

  if obj.Class.Name == "WillowPlayerPawn":
    return None

  try:
    arg_level = args.NewGameStage
  except:
    arg_level = args.NewInventoryGameStage
  
  level = get_pc().PlayerReplicationInfo.ExpLevel

  # edge case: don't down-level interactive objects in xmas area. it ruins christmas.
  if arg_level > level and setting != 3 and str(obj).startswith("WillowInteractiveObject'Xmas_P.TheWorld"):
    return
  #edge case: dont down-level interactive  objects in the TPS intro, no loot in atleast 1 chest
  if arg_level > level and setting != 3 and str(obj).startswith("WillowInteractiveObject'MoonShotIntro_P.TheWorld"):
    return


  with prevent_hooking_direct_calls():
    if setting == 1:
      func(level)
      return Block
    elif setting == 3 and arg_level < level:
      func(level)
      return Block
    elif setting == 2 and arg_level > level:
      func(level)
      return Block