import datetime
import unrealsdk
import unrealsdk.unreal as unreal
from unrealsdk.hooks import Type, Block, prevent_hooking_direct_calls

from mods_base import get_pc, Game, hook
from ui_utils import show_chat_message, show_hud_message
from BouncyLootGod.state import get_globals

if Game.get_current().name == "TPS":
    from BouncyLootGod.bl_tps.mission_names import mission_name_to_ue_str, mission_ue_str_to_name
else:
    from BouncyLootGod.bl2.mission_names import mission_name_to_ue_str, mission_ue_str_to_name

# TODO: move bl2 specific stuff to another file

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

    # only works for plot missions, but also makes plot missions work in FUM ¯\_(ツ)_/¯
    backup_level = mission_def.GameStage
    mission_def.GameStage = get_pc().PlayerReplicationInfo.ExpLevel

    r = mission_def.Reward
    ar = mission_def.AlternativeReward

    # add alternate as second option, duplicate main reward if there's only one
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

    # def reset_xp(r, backup_xp_struct, backup_level):
    r.ExperienceRewardPercentage = backup_xp_struct
    mission_def.GameStage = backup_level

    # if mission is opened after 5 seconds, it will display the xp amount, but not reward that amount.
    # call_later(5, lambda r=r, backup_xp_struct=backup_xp_struct: reset_xp(r, backup_xp_struct, backup_level))

    # if len(mission_def.Reward.RewardItemPools or []) == 0 and len(mission_def.Reward.RewardItems or []) == 0:
    # get_pc().ShowStatusMenu()

def mission_is_complete(mission_def):
    pc = get_pc()
    if isinstance(mission_def, str):
        mission_def = unrealsdk.find_object("MissionDefinition", mission_def)
        print(mission_def)
    playthrough = pc.GetCurrentPlaythrough()
    mission_list = pc.MissionPlaythroughs[playthrough].MissionList
    mission_data = next((x for x in mission_list if x.MissionDef == mission_def), None)
    if not mission_data:
        print("asdf")
        return False
    if mission_data.GameStage <= 0:
        print(mission_def)
        return False

    return mission_data.Status == 4 # unrealsdk.find_enum("EMissionStatus")["MS_Complete"]

def all_missions_complete(mission_list):
    for m in mission_list:
        if not mission_is_complete(m):
            return False
    return True

windshear_plot_missions = (
    "GD_Episode01.M_Ep1_Champion",
    "GD_Episode02.M_Ep2_Henchman",
)

def place_windshear_plot_missions():
    bounty_board = unrealsdk.find_object("Object" ,"Glacial_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_258") # button
    directives = unrealsdk.construct_object("MissionDirectivesDefinition", bounty_board)
    did_add_mission = False
    for m_str in windshear_plot_missions:
        m = unrealsdk.find_object("MissionDefinition", m_str)
        print(m)
        print(m.GameStage)
        if m.GameStage == -1:
            did_add_mission = True
            m.bRepeatable = True
            directives.MissionDirectives.append(unrealsdk.make_struct("MissionDirectorData", MissionDefinition=m, bBeginsMission=True, bEndsMission=True))

            # extra setup for My First Gun
            if m.Name == "M_Ep1_Champion":
                #  TODO: seems to not work every time.
                cabinet = unrealsdk.find_object("Object" ,"Glacial_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_285")
                # cabinet.ChangeInstanceDataSwitch("DoorsClosed_NotGlowing", 1)
                cabinet.ChangeInstanceDataSwitch("DoorsOpen_NotGlowing", 0)
                crbss = unrealsdk.find_object("Behavior_ChangeRemoteBehaviorSequenceState", "GD_Episode01Data.InteractiveObjects.Ep1_WeaponLocker:BehaviorProviderDefinition_0.Behavior_ChangeRemoteBehaviorSequenceState_6")
                crbss.SequenceName = "Enabled"
                crbss.ApplyBehaviorToContext(cabinet, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
        else:
            m.bRepeatable = False

    if did_add_mission:
        bounty_board.Directives = directives
        bounty_board.ChangeInstanceDataSwitch("GlowSwitch", 1)
        bounty_board.RegisterMissionDirector()
        # don't let the button disable after being pressed
        crbss = unrealsdk.find_object("Behavior_ChangeRemoteBehaviorSequenceState", "Glacial_Dynamic.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_53.Behavior_ChangeRemoteBehaviorSequenceState_59")
        crbss.SequenceName = "Enabled"
        # re-enable button in case it was pressed before already
        crbss.ApplyBehaviorToContext(bounty_board, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))

    # first_gun = unrealsdk.find_object("MissionDefinition", "GD_Episode01.M_Ep1_Champion")



    # if first_gun.GameStage == -1:
    #     bounty_board.ChangeInstanceDataSwitch("GlowSwitch", 1)
    #     first_gun.bRepeatable = True
    #     # remove next mission from the cabinet
    #     cabinet = unrealsdk.find_object("Object" ,"Glacial_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_285")
        
    #     crbss = unrealsdk.find_object("Behavior_ChangeRemoteBehaviorSequenceState", "GD_Episode01Data.InteractiveObjects.Ep1_WeaponLocker:BehaviorProviderDefinition_0.Behavior_ChangeRemoteBehaviorSequenceState_6")
    #     crbss.SequenceName = "Enabled"

    #     cabinet.Directives.MissionDirectives[1].bBeginsMission = False
    #     cabinet.Directives.MissionDirectives[0].bBeginsMission = True
    #     cabinet.ChangeInstanceDataSwitch("DoorsClosed_NotGlowing", 1)
    #     cabinet.ChangeInstanceDataSwitch("DoorsOpen_NotGlowing", 0)
    #     cabinet.ChangeInstanceDataSwitch("Glow", 1)
    #     crbss.ApplyBehaviorToContext(cabinet, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
    #     # cabinet.SetUsability(True, 0)

    #     bpd = cabinet.InteractiveObjectDefinition.BehaviorProviderDefinition
    #     handle = unrealsdk.make_struct("BehaviorConsumerHandle", PID=cabinet.ConsumerHandle.PID)
    #     kernel = unrealsdk.find_object("BehaviorKernel", "GearboxFramework.Default__BehaviorKernel")
    #     kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Enabled", 1) # EChangeStatus.CHANGE_Enable == 1
    #     kernel.ChangeBehaviorSequenceActivationStatus(handle, bpd, "Disabled", 2) # EChangeStatus.CHANGE_Disable == 2

    # else:
    #     cabinet.Directives.MissionDirectives[1].bBeginsMission = True
    #     cabinet.Directives.MissionDirectives[0].bBeginsMission = False
    #     first_gun.bRepeatable = False

    # blindsided = unrealsdk.find_object("MissionDefinition", "GD_Episode02.M_Ep2_Henchman")
    # print("blindsided.GameStage: " + str(blindsided.GameStage))

    # if blindsided.GameStage == -1:
    #     blindsided.bRepeatable = True
    #     bounty_board.ChangeInstanceDataSwitch("GlowSwitch", 1)
    #     directives = unrealsdk.construct_object("MissionDirectivesDefinition", bounty_board)
    #     directives.MissionDirectives.append(unrealsdk.make_struct("MissionDirectorData", MissionDefinition=blindsided, bBeginsMission=True, bEndsMission=True))
    #     bounty_board.Directives = directives
    #     bounty_board.RegisterMissionDirector()
    #     # don't let the button disable after being pressed
    #     crbss = unrealsdk.find_object("Behavior_ChangeRemoteBehaviorSequenceState", "Glacial_Dynamic.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_53.Behavior_ChangeRemoteBehaviorSequenceState_59")
    #     crbss.SequenceName = "Enabled"
    #     crbss.ApplyBehaviorToContext(bounty_board, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters")) # re-enable button in case it was pressed before mod was enabled.
    # else:
    #     blindsided.bRepeatable = False

    # first_gun = unrealsdk.find_object("MissionDefinition", "GD_Episode01.M_Ep1_Champion")
    # print("first_gun.GameStage: " + str(first_gun.GameStage))




southern_shelf_plot_missions = (
    # "GD_Episode02.M_Ep2a_MoreGuns", # Cleaning up the Berg - Southern Shelf intro - claptrap doesn't show up
    "GD_Episode02.M_Ep2c_Henchman",
    "GD_Episode03.M_Ep3_CatchARide",
)

def place_southern_shelf_plot_missions():
    # TODO: runs too early. maybe move to "Touch"
    bounty_board = unrealsdk.find_object("Object" ,"SouthernShelf_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_673")
    directives = bounty_board.Directives.MissionDirectives
    for m_str in southern_shelf_plot_missions:
        m = unrealsdk.find_object("MissionDefinition", m_str)
        if m.GameStage == -1:
            m.bRepeatable = True
        else:
            m.bRepeatable = False

        existing = next((x for x in directives if x.MissionDefinition == m), None)
        if not existing:
            directives.append(unrealsdk.make_struct("MissionDirectorData", MissionDefinition=m, bBeginsMission=True, bEndsMission=True))
        else:
            existing.bBeginsMission = True
            existing.bEndsMission = True
    bounty_board.RegisterMissionDirector()

sanctuary_plot_missions = (
    # "GD_Episode04.M_Ep4_WelcomeToSanctuary", # Plan B - Just wandering Sanctuary, doesn't work as expected
    "GD_Episode05.M_Ep5_ThePhoenix",
    "GD_Episode06.M_Ep6_RescueRoland",
    "GD_Episode07.M_Ep7_ATrainToCatch",
    # "GD_Episode08.M_Ep8_SanctuaryTakesOff", # Rising Action - Cutscene, works strange
    "GD_Episode09.M_Ep9_GetBackToSanctuary",
    "GD_Episode10.M_Ep10_BirdISTheWord",
    "GD_Episode11.M_Ep11_LikeATonOf",
    "GD_Episode12.M_Ep12_BecomingJack",
    "GD_Episode13.M_Ep13_KillAngel",
    # "GD_Episode14.M_Ep14_SearchingTheWreckage", # Where Angels Fear to Tread (Part 2) - Single Objective only
    "GD_Episode16.M_Ep16_LockAndLoad",
    "GD_Episode15.M_Ep15_CharacterAssassination",
    # "GD_Episode17.M_Ep17_KillJack",
)

def move_sanctuary_blocked_missions():
    blg = get_globals()
    pc = get_pc()
    try:
        bounty_board = unrealsdk.find_object("Object" ,"SanctuaryAir_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_8")
    except:
        pass
    try:
        if not bounty_board:
            bounty_board = unrealsdk.find_object("Object" ,"Sanctuary_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_8")
    except:
        print("move_sanctuary_blocked_missions: call me in sanctuary.")

    if blg.settings.get("fully_unlocked_mode", 0) == 0:
        blocked_missions = blg.blocked_missions
        # remove BlockedMissions from active quest. This is a destructive action which is only restored when restarting the game (not save-quit)
        # TODO blocked missions also available in pc.WorldInfo.GRI.MissionTracker.BlockedMissions, unsure if you can accept them without removing them from active mission
        active_mission = pc.WorldInfo.GRI.MissionTracker.GetActiveMission()
        current_blocked_missions = active_mission.BlockedMissions if active_mission else None
        if current_blocked_missions and not all_missions_complete(current_blocked_missions):
            blg.blocked_missions = []
            for m in current_blocked_missions:
                blg.blocked_missions.append(m)
            active_mission.BlockedMissions = []
            show_chat_message("blocked missions detected, save-quit to make them appear at the bounty board")
    else:
        blocked_missions = [unrealsdk.find_object("MissionDefinition", x) for x in possibly_blocked_quests]

    if blocked_missions:
        for m in blocked_missions:
            print(blocked_missions)
            directives = bounty_board.Directives.MissionDirectives
            is_in_list = next((x for x in directives if x.MissionDefinition == m), None)
            if not is_in_list:
                directives.append(unrealsdk.make_struct("MissionDirectorData", MissionDefinition=m, bBeginsMission=True, bEndsMission=True))



def place_sanctuary_plot_missions():
    try:
        bounty_board = unrealsdk.find_object("Object" ,"SanctuaryAir_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_8")
    except:
        pass
    try:
        bounty_board = unrealsdk.find_object("Object" ,"Sanctuary_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_8")
    except:
        print("place_sanctuary_plot_missions: call me in sanctuary.")

    # also allow all story missions to be turned in here
    for m_str in sanctuary_plot_missions:
        if m.GameStage == -1:
            m.bRepeatable = True
        else:
            m.bRepeatable = False

        m = unrealsdk.find_object("MissionDefinition", m_str)
        directives = bounty_board.Directives.MissionDirectives
        is_in_list = next((x for x in directives if x.MissionDefinition == m), None)
        if not is_in_list:
            directives.append(unrealsdk.make_struct("MissionDirectorData", MissionDefinition=m, bBeginsMission=True, bEndsMission=True))
    bounty_board.RegisterMissionDirector()


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

# TODO: this is currently basegame only
def remove_story_mission_deps():
    kill_jack: unreal.UObject = unrealsdk.find_object("MissionDefinition", "GD_Episode17.M_Ep17_KillJack")
    # base game
    for mission in unrealsdk.find_all("MissionDefinition"):
        if mission.GameStageRegion and mission.GameStageRegion.DlcExpansion:
            # skip missions for now
            continue
        if mission == kill_jack:
            mission.BlockedMissions = ()
            continue
        elif mission.bPlotCritical:
            # modify plot missions
            mission.Dependencies = ()
            mission.BlockedMissions = ()
            mission.NextMissionInChain = kill_jack
        else:
            # modify everything else to not depend on plot missions
            mission.Dependencies = tuple(
                dependency for dependency in mission.Dependencies if not dependency.bPlotCritical
            )

            # pn = mission.PathName(mission)
            # if pn in sanctuary_plot_missions:
            #     plot_missions.append(mission)

    # if kill_jack:
    #     # make final mission have all plot deps
    #     # pms = [unrealsdk.find_object("MissionDefinition", m) for m in sanctuary_plot_missions]
    #     pms = list()

    #     for plot_mission in sanctuary_plot_missions + windshear_plot_missions + southern_shelf_plot_missions:
    #         pm = unrealsdk.find_object("MissionDefinition", plot_mission)
    #         if pm == kill_jack:
    #             continue
    #         pm.NextMissionInChain = kill_jack
    #         pms.append(pm)
    #     kill_jack.Dependencies = pms


possibly_blocked_quests = (
    "GD_Z1_ClapTrapStash.M_ClapTrapStash",
    "GD_Z2_ClaptrapBirthdayBash.M_ClaptrapBirthdayBash",
    "GD_Z2_HyperionStatue.M_MonumentsVandalism",
    "GD_Z1_ChildrenOfPhoenix.M_EternalFlame",
    "GD_Z1_ChildrenOfPhoenix.M_FalseIdols",
    "GD_Z1_ChildrenOfPhoenix.M_LightingTheMatch",
    "GD_Z1_ChildrenOfPhoenix.M_TheEnkindling",
    "GD_Z1_InMemoriam.M_InMemoriam",
    "GD_Z1_MineAllMine.M_MineAllMine",
    "GD_Z2_HomeMovies.M_HomeMovies",
    "GD_Z1_TrainRobbery.M_TrainRobbery",
    "GD_Z2_Rakkaholics.M_Rakkaholics",
    "GD_Z1_BearerBadNews.M_BearerBadNews",
    "GD_Z2_FreeWilly.M_FreeWilly",
    "GD_Z3_ThisJustIn.M_ThisJustIn",
)

@hook('WillowGame.MissionTracker:UpdateObjective')
def block_objectives_story_final(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # GD_Episode17.M_Ep17_KillJack
    blg = get_globals()
    if blg.settings.get("fully_unlocked_mode", 0) == 0:
        return

    if args.MissionObjective.Outer.Name == "M_Ep17_KillJack":
        if not all_missions_complete(windshear_plot_missions + southern_shelf_plot_missions + sanctuary_plot_missions):
            show_chat_message("You must finish all base game plot missions to continue Talon of God!")
            return Block
    # doing this means we need to move all of claptrap's quests elsewhere
    # print(obj)

@hook('WillowGame.WillowPlayerController:AcceptMission')
def accept_mission(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # print(obj)
    # print(args)
    # print("extAcceptConfirmed")
    # idx = obj.GetSelectedIndex()
    # mission = obj.MissionList[idx]
    # mission_def = mission.MissionDef

    print(args.Mission)
    if args.Mission.Name == "M_Ep2_Henchman":
        show_chat_message("Save-quit to begin Blindsided")
    elif args.Mission.Name == "M_Ep2c_Henchman":
        show_chat_message("Save-quit to make claptrap appear for Best Minion Ever")
        # TODO issue with ending - boat is invisible, still has collision, but the waypoint can be hard to hit
        # GD_Episode02.M_Ep2c_Henchman:BoardClaptapsVessel

    # return Block

@hook("WillowGame.WillowPlayerController:ServerCompleteMission", Type.POST)
def complete_plot_mission(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # mission_def.bRepeatable = False
    print("ServerCompleteMission")
    if args.Mission.bPlotCritical:
        args.Mission.bRepeatable = False

mission_hooks = [
    accept_mission,
    complete_plot_mission,
    block_objectives_story_final,
]


# useful for testing, you can repeat digi peak quest
# set GD_Lobelia_UnlockDoor.M_Lobelia_UnlockDoor bRepeatable True
# !getitem questrewarddrtandthevaulthunters