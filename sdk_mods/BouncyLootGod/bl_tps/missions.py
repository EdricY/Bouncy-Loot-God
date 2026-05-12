import datetime
import unrealsdk
import unrealsdk.unreal as unreal
from unrealsdk.hooks import Type

from mods_base import get_pc
from ui_utils import show_chat_message, show_hud_message
from BouncyLootGod.state import get_globals


mission_name_to_ue_str = {
    "Welcome to Helios":                                  "GD_Co_Chapter01.M_CH01a_MoonShot",
    "Systems Jammed":                                     "GD_Co_Chapter03.M_Co_Ch03_Concordia",
    "Eye to Eye":                                         "GD_Co_LaserRebootMission.M_LaserRebootMission",
    "Last Requests":                                      "GD_Co_LastRequests.M_LastRequests",
    "Boarding Party":                                     "GD_Co_Boarding_Party.M_BoardingParty",
    "Lost Legion Invasion":                               "GD_Co_Chapter01.M_CH01b_MoonShot",
    "Marooned":                                           "GD_Co_Chapter02.M_CH02_Airstrip",
    "A New Direction":                                    "GD_Co_Chapter04.M_Co_Chapter04",
    "Intelligences of the Artificial Persuasion":         "GD_Co_Chapter05.M_Cork_WreckMain",
    "The Beginning of the End":                           "GD_Co_Chapter11.M_DahlDigsite",
    "Cleanliness Uprising":                               "GD_Co_Cleanliness_Uprising.M_Cleanliness_Uprising",
    "The Bestest Story Ever Told":                        "GD_Co_CorkRaid.M_CorkRaid",
    "An Urgent Message":                                  "GD_Co_Detention.M_Detention",
    "Don't Shoot the Messenger":                          "GD_Co_DontShootMessenger.MissionDef.M_DontShootMsgr",
    "The Empty Billabong":                                "GD_Co_EmptyBillabong.M_EmptyBillaBong",
    "Follow Your Heart":                                  "GD_Co_FollowYourHeart.M_FollowYourHeart",
    "Guardian Hunter":                                    "GD_Co_GuardianHunter.MissionDef.M_GuardianHunter",
    "Sterwin Forever":                                    "GD_Co_GuardianHunter.MissionDef.M_SterwinForever",
    "Home Delivery":                                      "GD_Co_HomeDelivery.M_HomeDelivery",
    "Hot Head":                                           "GD_Co_Hot_Head.M_Hot_Head",
    "Bunch of Ice Holes":                                 "GD_Co_IceHoles.M_Co_IceHoles",
    "Kill Meg":                                           "GD_Co_Kill_Meg.M_Kill_Meg",
    "DAHL Combat Training: Round 1":                      "GD_Co_MoonSlaughter.M_Co_MoonSlaughter01",
    "Land Among the Stars":                               "GD_Co_Motivation.M_Motivation",
    "Nova? No Problem!":                                  "GD_Co_NovaNoProblem.M_NovaNoProblem",
    "Paint Job":                                          "GD_Co_Paint_Job.M_Paint_Job",
    "Pop Racing":                                         "GD_Co_PopRacing.M_Co_PopRacing",
    "Handsome AI":                                        "GD_Co_PushButtonMission.M_PushButtonMission",
    "Return of Captain Chef":                             "GD_Co_ReturnOfCapnChef.M_ReturnOfCaptainChef",
    "Rough Love":                                         "GD_Co_RoughLove.M_Co_RoughLove",
    "The Secret Chamber":                                 "GD_Co_SecretChamber.M_SecretChamber",
    "To the Moon":                                        "GD_Co_Side_EngineerMoonShot.M_EngineerMoonShot",
    "Things That Go Boom":                                "GD_Co_Side_Exploders.M_Exploders",
    "Fresh Air":                                          "GD_Co_Side_FreshAir.M_FreshAir",
    "Lab 19":                                             "GD_Co_Side_Lab19.M_Lab19",
    "Lock and Load":                                      "GD_Co_Side_LockAndLoad.M_LockAndLoad",
    "Infinite Loop":                                      "GD_Co_Side_Loop.M_InfiniteLoop",
    "Picking Up the Pieces":                              "GD_Co_Side_PickingUp.M_PickingUpThePieces",
    "Red, Then Dead":                                     "GD_Co_Side_Reshirt.M_RedShirt",
    "It Ain't Rocket Surgery":                            "GD_Co_Side_RocketSurgery.M_RocketSurgery",
    "The Don":                                            "GD_Co_Side_TheDon.M_TheDon",
    "These are the Bots":                                 "GD_Co_Side_TheseAreTheBots.M_TheseAreTheBots",
    "Z8N-TP":                                             "GD_Co_Side_Z8MTRP.M_Z8nTRP",
    "Space Slam":                                         "GD_Co_SpaceSlam.M_SpaceSlam",
    "Sub-Level 13":                                       "GD_Co_SubLevel13.M_Co_SubLevel13Part1",
    "Sub-Level 13: Part 2":                               "GD_Co_SubLevel13.M_Co_SubLevel13Part2",
    "Tales from Elpis":                                   "GD_Co_TalesFromElpis.M_TalesFromElpis",
    "To Arms!":                                           "GD_Co_ToArms.M_Co_ToArms",
    "Torgue-o! Torgue-o!":                                "GD_Co_ToroToro.M_ToroToro",
    "Treasures of ECHO Madre":                            "GD_Co_TreasuresofECHO.M_Co_TreasuresofECHO",
    "Voice Over":                                         "GD_Co_VoiceOver.M_VoiceOver",
    "The Voyage of Captain Chef":                         "GD_Co_VoyageOfCaptainChef.M_VoyageOfCaptainChef",
    "Wherefore Art Thou?":                                "GD_Co_WhereforeArtThou.M_Co_WhereforeArtThou",
    "Wiping the Slate":                                   "GD_Co_WipingSlate.M_WipingSlate",
    "Nothing is Never an Option":                         "GD_Co_YouAskHowHigh.M_Co_YouAskHowHigh",
    "Zapped 1.0":                                         "GD_Co_Zapped.M_Co_Zapped1",
    "Zapped 2.0":                                         "GD_Co_Zapped.M_Co_Zapped2",
    "Zapped 3.0":                                         "GD_Co_Zapped.M_Co_Zapped3",
    "All the Little Creatures":                           "gd_cork_allthelittlecreatures.M_AllTheLittleCreatures",
    "Another Pickle":                                     "GD_Cork_AnotherPickle.M_Cork_AnotherPickle",
    "Quarantine: Back On Schedule":                       "GD_Cork_BackOnSchedule.M_BackOnSchedule",
    "Let's Build a Robot Army":                           "GD_Cork_DahlFactory_Plot.M_Cork_DahlFactory_Plot",
    "Don't Get Cocky":                                    "GD_Cork_DontGetCocky.M_DontGetCocky",
    "Eradicate!":                                         "GD_Cork_Eradicate.M_Eradicate",
    "Grinders":                                           "GD_Cork_Grinding.M_Cork_Grinding",
    "Home Sweet Home":                                    "GD_Cork_HeliosFoothold_Plot.M_Cork_HeliosFoothold",
    "Watch Your Step":                                    "GD_Cork_InnerHull_Plot.M_Cork_InnerHull",
    "In Perfect Hibernation":                             "GD_Cork_PerfectHibernation.M_PerfectHibernation",
    "Quarantine: Infestation":                            "GD_Cork_Quarantine.M_Quarantine",
    "Science and Violence":                               "GD_Cork_RandDFacility_Plot.M_Cork_RandDFacility",
    "Recruitment Drive":                                  "GD_Cork_Resistors.M_Resistors",
    "No Such Thing as a Free Launch":                     "GD_Cork_Rocketeering.M_Rocketeering",
    "Trouble with Space Hurps":                           "GD_Cork_TroubleWithSpaceHurps.M_TroubleWithSpaceHurps",
    "DAHL Combat Training: Round 2":                      "GD_Co_MoonSlaughter.M_Co_MoonSlaughter02",
    "DAHL Combat Training: Round 3":                      "GD_Co_MoonSlaughter.M_Co_MoonSlaughter03",
    "DAHL Combat Training: Round 4":                      "GD_Co_MoonSlaughter.M_Co_MoonSlaughter04",
    "DAHL Combat Training: Round 5":                      "GD_Co_MoonSlaughter.M_Co_MoonSlaughter05",
    "Boomshakalaka":                                      "GD_Co_Boomshakalaka.M_Boomshakalaka",
    "Alpha":                                              "GD_SparkMissions.SparkMissionAlpha",
    "Beta":                                               "GD_SparkMissions.SparkMissionBeta",
    "Delta":                                              "GD_SparkMissions.SparkMissionDelta",
    "Gamma":                                              "GD_SparkMissions.SparkMissionGamma",
    "l33t h4X0rz":                                        "GD_Ma_Side_H4X0rz.M_Ma_Side_H4X0rz_Repeat",
    "Enter the Claptrap":                                 "GD_Ma_Chapter02.M_Ma_Chapter02",
    "File Search":                                        "GD_Ma_Chapter03.M_Ma_Chapter03",
    "END OF LINE":                                        "GD_Ma_Chapter05.M_Ma_Chapter05",
    "System Shutdown":                                    "GD_Ma_Chapter06.M_Ma_Chapter06",
    "The Psychology of a Claptrap":                       "GD_Ma_RightBrainCluster.M_Ma_RightCluster",
    "A Deadlier Game":                                    "GD_Ma_Side_BadTrap.M_Ma_Side_BadTrap",
    "Byte Club":                                          "GD_Ma_Side_ByteClub.M_Ma_Side_ByteClub",
    "Chip's Data Mining Adventure":                       "GD_Ma_Side_CookieDataMining.M_Ma_Side_CookieDataMining",
    "3G0-TP":                                             "GD_Ma_Side_EgoTrap.M_Ma_Side_EgoTrap",
    "1D-TP":                                              "GD_Ma_Side_IdTrap.M_Ma_Side_IdTrap",
    "Rose Tinting":                                       "GD_Ma_Side_MINAC.M_Ma_Side_MINAC",
    "Corrosion of Dignity":                               "GD_Ma_Side_ShredOfDignity.M_Ma_Side_ShredOfDignity",
    "Spyware Who Came in from the Cold":                  "GD_Ma_Side_SpywareInFromCold.M_Ma_Side_SpywareInFromCold",
    "You Can Stop the Music":                             "GD_Ma_Side_StopTheMusic.M_Ma_Side_StopTheMusic",
    "The Sum of Some Fears":                              "GD_Ma_Side_SumOfSomeFears.M_Ma_Side_SumOfSomeFears",
    "5UP4-3G0-TP":                                        "GD_Ma_Side_SuperEgoTrap.M_Ma_Side_SuperEgoTrap",
    "The Temple of Boom":                                 "GD_Ma_Side_TempleOfBoom.M_Ma_Side_TempleofBoom",
    "h4X0rz":                                             "GD_Ma_Side_H4X0rz.M_Ma_Side_H4X0rz",
    "Digistructed Madness: Round 1":                      "GD_EridianSlaughter.MissionDef.M_EridianSlaughter01",
    "Digistructed Madness: Round 2":                      "GD_EridianSlaughter.MissionDef.M_EridianSlaughter02",
    "Digistructed Madness: Round 3":                      "GD_EridianSlaughter.MissionDef.M_EridianSlaughter03",
    "Digistructed Madness: Round 4":                      "GD_EridianSlaughter.MissionDef.M_EridianSlaughter04",
    "Digistructed Madness: Round 5":                      "GD_EridianSlaughter.MissionDef.M_EridianSlaughter05",
    "Digistructed Madness: The Badass Round":             "GD_EridianSlaughter.MissionDef.M_EridianSlaughter_Badass",
}

mission_ue_str_to_name = {v.split('.')[-1]: k for k, v in mission_name_to_ue_str.items()}

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