import datetime
import unrealsdk
import unrealsdk.unreal as unreal
from unrealsdk.hooks import Type

from mods_base import get_pc, Game
from ui_utils import show_chat_message, show_hud_message
from BouncyLootGod.state import get_globals

if Game.get_current().name == "TPS":
    from BouncyLootGod.bl_tps.mission_names import mission_name_to_ue_str, mission_ue_str_to_name
else:
    from BouncyLootGod.bl2.mission_names import mission_name_to_ue_str, mission_ue_str_to_name


def call_later(time, call):
    """Call the given callable after the given time has passed."""
    timer = datetime.datetime.now()
    future = timer + datetime.timedelta(seconds=time)

    # Create a wrapper to call the routine that is suitable to be passed to add_hook.
    def tick(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
        # Invoke the routine when enough time has passed and unregister its tick hook.
        if datetime.datetime.now() >= future:
            call()
            unrealsdk.hooks.remove_hook("WillowGame.WillowGameViewportClient:Tick", Type.PRE, "CallLater" + str(call))
        return True

    # Hook the wrapper.
    unrealsdk.hooks.add_hook("WillowGame.WillowGameViewportClient:Tick", Type.PRE, "CallLater" + str(call), tick)

# # unused for now
# def temp_set_prop(obj, prop_name, val, time=1):
#     backup = getattr(obj, prop_name)
#     if backup == val:
#         print(prop_name + " already set to val")
#         return
#     setattr(obj, prop_name, val)
#     def reset_prop(obj, prop_name, backup):
#         setattr(obj, prop_name, backup)
#     call_later(time, lambda obj=obj, prop_name=prop_name, backup=backup: reset_prop(obj, prop_name, backup))


def grant_mission_reward(mission_name) -> None:
    ue_str = mission_name_to_ue_str.get(mission_name)
    if not ue_str:
        print("unknown mission: " + mission_name)
        show_chat_message("unknown mission: " + mission_name)
        return
    mission_def = unrealsdk.find_object("MissionDefinition", ue_str)
    # mission_def.GameStage = get_pc().PlayerReplicationInfo.ExpLevel

    r = mission_def.Reward
    ar = mission_def.AlternativeReward

    # duplicate reward if there's only one
    if sum(x is not None for x in r.RewardItems or []) == 1:
        if len(ar.RewardItems):
            extra = ar.RewardItems[0]
        else:
            extra = r.RewardItems[0]
        r.RewardItems = [r.RewardItems[0], extra]
    elif sum(x is not None for x in r.RewardItemPools or []) == 1:
        if len(ar.RewardItemPools):
            extra = ar.RewardItemPools[0]
        else:
            extra = r.RewardItemPools[0]
        r.RewardItemPools = [r.RewardItemPools[0], extra]

    backup_xp_struct = unrealsdk.make_struct("AttributeInitializationData",
        BaseValueConstant = r.ExperienceRewardPercentage.BaseValueConstant,
        BaseValueAttribute = r.ExperienceRewardPercentage.BaseValueAttribute,
        InitializationDefinition = r.ExperienceRewardPercentage.InitializationDefinition,
        BaseValueScaleConstant = r.ExperienceRewardPercentage.BaseValueScaleConstant,
    )
    r.ExperienceRewardPercentage = unrealsdk.make_struct("AttributeInitializationData", 
        BaseValueConstant=0,
        BaseValueAttribute=None,
        InitializationDefinition=None,
        BaseValueScaleConstant=0
    )
    show_hud_message("Quest Reward Received", mission_name, 4)
    get_pc().ServerGrantMissionRewards(mission_def, False)
    def reset_xp(r, backup_xp_struct):
        r.ExperienceRewardPercentage = backup_xp_struct

    # if mission is opened after 5 seconds, it will display the xp amount, but not reward that amount.
    call_later(5, lambda r=r, backup_xp_struct=backup_xp_struct: reset_xp(r, backup_xp_struct))

    # if len(mission_def.Reward.RewardItemPools or []) == 0 and len(mission_def.Reward.RewardItems or []) == 0:
    # get_pc().ShowStatusMenu()

def mission_is_complete(mission_def):
    pc = get_pc()
    playthrough = pc.GetCurrentPlaythrough()
    mission_list = pc.MissionPlaythroughs[playthrough].MissionList
    mission_data = next((x for x in mission_list if x.MissionDef == mission_def), None)
    if not mission_data:
        return False

    return mission_data.Status == 4 # unrealsdk.find_enum("EMissionStatus")["MS_Complete"]

def all_missions_complete(mission_list):
    for m in mission_list:
        if not mission_is_complete(m):
            return False
    return True

def move_sanctuary_blocked_missions():
    blg = get_globals()
    try:
        bounty_board = unrealsdk.find_object("Object" ,"SanctuaryAir_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_8")
    except:
        print("move_sanctuary_blocked_missions: call me in sanctuary_air.")
        return

    if blg.blocked_missions:
        for m in blg.blocked_missions:
            directives = bounty_board.Directives.MissionDirectives
            is_in_list = next((x for x in directives if x.MissionDefinition == m), None)
            if not is_in_list:
                directives.append(unrealsdk.make_struct("MissionDirectorData", MissionDefinition=m, bBeginsMission=True, bEndsMission=True))
        bounty_board.RegisterMissionDirector()

    # remove BlockedMissions from active quest. This is a destructive action which is only restored when restarting the game (not save-quit)
    active_mission = get_pc().WorldInfo.GRI.MissionTracker.GetActiveMission()
    current_blocked_missions = active_mission.BlockedMissions
    if current_blocked_missions and not all_missions_complete(current_blocked_missions):
        blg.blocked_missions = []
        for m in current_blocked_missions:
            blg.blocked_missions.append(m)
        active_mission.BlockedMissions = []
        show_chat_message("blocked missions detected, save-quit to make them appear at the bounty board")

    # try:
    #     # impossible to talk to brick for bearer of bad news 
    #     get_pc().WorldInfo.GRI.MissionTracker.UpdateObjective(unrealsdk.find_object("MissionObjectiveDefinition", "GD_Z1_BearerBadNews.M_BearerBadNews:TalkBrick"))
    # except:
    #     pass

def move_southern_shelf_blocked_missions():
    bounty_board = unrealsdk.find_object("Object" ,"SouthernShelf_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_673")
    if not bounty_board or not bounty_board.Directives:
        print("bounty_board not ready")
        return
    directives = bounty_board.Directives.MissionDirectives
    missions = [
        unrealsdk.find_object("MissionDefinition", "GD_Episode02.M_Ep2b_Henchman"),
        unrealsdk.find_object("MissionDefinition", "GD_Z1_BadHairDay.M_BadHairDay"),
        unrealsdk.find_object("MissionDefinition", "GD_Z1_ThisTown.M_ThisTown"),
        unrealsdk.find_object("MissionDefinition", "GD_Z1_Symbiosis.M_Symbiosis"),
    ]
    for m in missions:
        existing = next((x for x in directives if x.MissionDefinition == m), None)
        if not existing:
            directives.append(unrealsdk.make_struct("MissionDirectorData", MissionDefinition=m, bBeginsMission=True, bEndsMission=True))
        else:
            existing.bBeginsMission = True
            existing.bEndsMission = True
    bounty_board.RegisterMissionDirector()

    try:
        # turn in Bad Hair Day to Hammerlock
        get_pc().WorldInfo.GRI.MissionTracker.UpdateObjective(unrealsdk.find_object("MissionObjectiveDefinition", "GD_Z1_BadHairDay.M_BadHairDay:ReturnToHammerlock"))
    except:
        pass

# useful for testing, you can repeat digi peak quest
# set GD_Lobelia_UnlockDoor.M_Lobelia_UnlockDoor bRepeatable True
# !getitem questrewarddrtandthevaulthunters