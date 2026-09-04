import random
import unrealsdk
import unrealsdk.unreal as unreal
from mods_base import get_pc, build_mod, hook
from unrealsdk.hooks import Block, Type
from BouncyLootGod.state import get_globals, game_is_bl2


# TODO: how does this work with dlc uninstalled
raw_mission_data = [
    {"MissionDef": 'GD_Episode01.M_Ep1_Champion', "Status": 4, "ObjectivesProgress": [1], "GameStage": -1},
    {"MissionDef": 'GD_Episode02.M_Ep2_Henchman', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,1,0,1,1], "GameStage": -1},
    {"MissionDef": 'GD_Episode02.M_Ep2a_MoreGuns', "Status": 4, "ObjectivesProgress": [0,1,1,1,1,1,1], "GameStage": -1},
    {"MissionDef": 'GD_Episode02.M_Ep2c_Henchman', "Status": 4, "ObjectivesProgress": [1,1,0,1,1,1,0,1,1,1,1,1,1,1], "GameStage": -1},
    {"MissionDef": 'GD_Episode03.M_Ep3_CatchARide', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,1,1,3,1,20,1,1,1,1], "GameStage": -1},
    {"MissionDef": 'GD_Episode04.M_Ep4_WelcomeToSanctuary', "Status": 4, "ObjectivesProgress": [1,1,3,1,1,0,1,1,1,1,1,1], "GameStage": -1},
    {"MissionDef": 'GD_Episode05.M_Ep5_ThePhoenix', "Status": 4, "ObjectivesProgress": [1,1,7,1,1,1,1,1,1,1], "GameStage": -1},
    {"MissionDef": 'GD_Episode06.M_Ep6_RescueRoland', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,1,5,1,1,1,1,1,1,1,1,1,0,0,0], "GameStage": -1},
    {"MissionDef": 'GD_Episode07.M_Ep7_ATrainToCatch', "Status": 4, "ObjectivesProgress": [1,1,1,0,3,1,1,3,1,0,3,3,3,1,1,1,1,1,1], "GameStage": -1},
    {"MissionDef": 'GD_Episode08.M_Ep8_SanctuaryTakesOff', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,1,481,1,1,1,1], "GameStage": -1},
    {"MissionDef": 'GD_Episode09.M_Ep9_GetBackToSanctuary', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,1,1,1,0,1,1,1,1,0], "GameStage": -1},
    {"MissionDef": 'GD_Episode10.M_Ep10_BirdISTheWord', "Status": 4, "ObjectivesProgress": [1,1,1,1,0,3,1,10,1,0,1], "GameStage": -1},
    {"MissionDef": 'GD_Episode11.M_Ep11_LikeATonOf', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,1,3], "GameStage": -1},
    {"MissionDef": 'GD_Episode12.M_Ep12_BecomingJack', "Status": 4, "ObjectivesProgress": [1,1,1,1,15,1,1], "GameStage": -1},
    {"MissionDef": 'GD_Episode13.M_Ep13_KillAngel', "Status": 4, "ObjectivesProgress": [1,1,0,1,1,1,1,1,11,1,3], "GameStage": -1},
    {"MissionDef": 'GD_Episode14.M_Ep14_SearchingTheWreckage', "Status": 4, "ObjectivesProgress": [1], "GameStage": -1},
    {"MissionDef": 'GD_Episode16.M_Ep16_LockAndLoad', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,4,1,1,1,1,1,1,1,5,15], "GameStage": -1},
    {"MissionDef": 'GD_Episode15.M_Ep15_CharacterAssassination', "Status": 4, "ObjectivesProgress": [1,1,1,3,1,33,1,3,1,1,1,1,1,1], "GameStage": -1},
    {"MissionDef": 'GD_Episode17.M_Ep17_KillJack', "Status": 1, "ObjectivesProgress": [1,1,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0], "ActiveObjectiveSet": 'GD_Episode17.M_Ep17_KillJack:LeaveSanctuarySet2', "SubObjectiveSets": [], "GameStage": 30, "bNeedsRewards": False, "bHeardKickoff": True},

    {"MissionDef": 'GD_Orchid_Plot.M_Orchid_PlotMission01', "Status": 4, "ObjectivesProgress": [1,1,1,1]}, 
    {"MissionDef": 'GD_Orchid_Plot_Mission02.M_Orchid_PlotMission02', "Status": 4, "ObjectivesProgress": [1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]},
    {"MissionDef": 'GD_Orchid_Plot_Mission03.M_Orchid_PlotMission03', "Status": 4, "ObjectivesProgress": [1,1,1,1]},
    {"MissionDef": 'GD_Orchid_Plot_Mission04.M_Orchid_PlotMission04', "Status": 4, "ObjectivesProgress": [1,1,1,1,1]},
    {"MissionDef": 'GD_Orchid_Plot_Mission05.M_Orchid_PlotMission05', "Status": 4, "ObjectivesProgress": [1,1,1,1,1]},
    {"MissionDef": 'GD_Orchid_Plot_Mission06.M_Orchid_PlotMission06', "Status": 4, "ObjectivesProgress": [0,15,1,1,1]},
    {"MissionDef": 'GD_Orchid_Plot_Mission07.M_Orchid_PlotMission07', "Status": 4, "ObjectivesProgress": [1,15,1,1,1,1,1,1]},
    {"MissionDef": 'GD_Orchid_Plot_Mission08.M_Orchid_PlotMission08', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,1,1,1,1,1,1]},
    {"MissionDef": 'GD_Orchid_Plot_Mission09.M_Orchid_PlotMission09', "Status": 1, "ObjectivesProgress": [1,2,1,0,0,0,0], "ActiveObjectiveSet": 'GD_Orchid_Plot_Mission09.M_Orchid_PlotMission09:KillPirateQueenSet', "GameStage": 20},

    {"MissionDef": 'GD_IrisEpisode01.M_IrisEp1_HighwayToHell', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,1,1]},
    {"MissionDef": 'GD_IrisEpisode01.M_IrisEp1_WTTJ', "Status": 4, "ObjectivesProgress": [1]},
    {"MissionDef": 'GD_IrisEpisode02.M_IrisEp2_CultOfPersonality', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,1,1]},
    {"MissionDef": 'GD_IrisEpisode02.M_IrisEp2_FindBattle', "Status": 4, "ObjectivesProgress": [1,1,1,1]},
    {"MissionDef": 'GD_IrisEpisode03_Battle.M_IrisEp3Battle_BarFight', "Status": 4, "ObjectivesProgress": [1,1]},
    {"MissionDef": 'GD_IrisEpisode03.M_IrisEp3_ChopSuey', "Status": 4, "ObjectivesProgress": [0,1,1]},
    {"MissionDef": 'GD_IrisEpisode04.M_IrisEp4_AMontage', "Status": 4, "ObjectivesProgress": [1,1,1]},
    {"MissionDef": 'GD_IrisEpisode04.M_IrisEp4_TrainningWithTina', "Status": 4, "ObjectivesProgress": [1,7,7,1]},
    {"MissionDef": 'GD_IrisEpisode04_Battle.M_IrisEp4Battle_Race', "Status": 4, "ObjectivesProgress": [1,1,1,1,0,1]},
    {"MissionDef": 'GD_IrisEpisode04.M_IrisEp4_CherryBomb', "Status": 4, "ObjectivesProgress": [1,0,1,1,1,1,1,1]},
    {"MissionDef": 'GD_IrisEpisode05.M_IrisEp5_CageMatch', "Status": 4, "ObjectivesProgress": [1,1,1,1]},
    {"MissionDef": 'GD_IrisEpisode05.M_HeavensDoor', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,1]},
    {"MissionDef": 'GD_IrisEpisode05_Battle.M_IrisEp5Battle_FlyboyGyro', "Status": 4, "ObjectivesProgress": [1,1,5]},
    {"MissionDef": 'GD_IrisEpisode05.M_IrisEp5_KickStartMyHeart', "Status": 4, "ObjectivesProgress": [1,0,0,0,1,1]},
    {"MissionDef": 'GD_IrisEpisode06.M_IrisEp6_LongWayToTheTop', "Status": 1, "ObjectivesProgress": [1,0,0,0,0], "ActiveObjectiveSet": 'GD_IrisEpisode06.M_IrisEp6_LongWayToTheTop:MissionObjectiveSetDefinition_9', "GameStage": 20},

    {"MissionDef": 'GD_Sage_Ep1.M_Sage_Mission01', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,1,1]}, 
    {"MissionDef": 'GD_Sage_Ep3.M_Sage_Mission03', "Status": 4, "ObjectivesProgress": [1,1,1,0,1,1]}, 
    {"MissionDef": 'GD_Sage_Ep4.M_Sage_Mission04', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,1,1,1,1]}, 
    {"MissionDef": 'GD_Sage_Ep5.M_Sage_Mission05', "Status": 1, "ObjectivesProgress": [1,0,1,1,1,1,0,0], "ActiveObjectiveSet": 'GD_Sage_Ep5.M_Sage_Mission05:KillBossSet', "GameStage": 35}, 

    {"MissionDef": 'GD_Aster_Plot_Mission01.M_Aster_PlotMission01', "Status": 4, "ObjectivesProgress": [1,0,0,1,1,0,0,1,0,1,1,3,1,1,1,1]},
    {"MissionDef": 'GD_Aster_Plot_Mission02.M_Aster_PlotMission02', "Status": 4, "ObjectivesProgress": [1,0,0,4,0,1,1,3,0,1,3,3,1,3,1,1,1,4]},
    {"MissionDef": 'GD_Aster_Plot_Mission03.M_Aster_PlotMission03', "Status": 4, "ObjectivesProgress": [1,0,10,0,1,1,1,1,1,15,1,1,0,1,1,1,0,15,1,1]},
    {"MissionDef": 'GD_Aster_Plot_Mission04.M_Aster_PlotMission04', "Status": 1, "ObjectivesProgress": [1,0,0,1,0,1,0,1,3,1,0,0,0,0], "ActiveObjectiveSet": 'GD_Aster_Plot_Mission04.M_Aster_PlotMission04:UseTeleporterSet', "GameStage": 35}, 

    {"MissionDef": 'GD_Anemone_Plot_Mission010.M_Anemone_PlotMission010', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,3,1,1]},
    {"MissionDef": 'GD_Anemone_Plot_Mission020.M_Anemone_PlotMission020', "Status": 4, "ObjectivesProgress": [1,1,3,8,1,4,1,0,0,1]},
    {"MissionDef": 'GD_Anemone_Plot_Mission025.M_Anemone_PlotMission025', "Status": 4, "ObjectivesProgress": [1,4,1,0,1,1,0,3,1,1,1,1,1]},
    {"MissionDef": 'GD_Anemone_Plot_Mission030.M_Anemone_PlotMission030', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,1,1,1,1,1]},
    {"MissionDef": 'GD_Anemone_Plot_Mission040.M_Anemone_PlotMission040', "Status": 4, "ObjectivesProgress": [1,1,1,25,1,2,2,1,2,2,1,1,1,1,1,1,1,1,1]},
    {"MissionDef": 'GD_Anemone_Plot_Mission050.M_Anemone_PlotMission050', "Status": 4, "ObjectivesProgress": [1,1,1,1,1,1,1,1,1,1,1,1,1]},
    {"MissionDef": 'GD_Anemone_Plot_Mission060.M_Anemone_PlotMission060', "Status": 1, "ObjectivesProgress": [1,1,0,1,1,0,0,0,0], "ActiveObjectiveSet": 'GD_Anemone_Plot_Mission060.M_Anemone_PlotMission060:Set_FindGaius02', "GameStage": 38}, 
]

def construct_mission_data():
    mission_data = []
    for rd in raw_mission_data:
        d = {**rd}
        if "MissionDef" in rd:
            d["MissionDef"] = unrealsdk.find_object("MissionDefinition", d["MissionDef"])
        if "ActiveObjectiveSet" in rd:
            d["ActiveObjectiveSet"] = unrealsdk.find_object("MissionObjectiveSetDefinition", rd["ActiveObjectiveSet"])
        mission_data.append(unrealsdk.make_struct("MissionStatusPlayerData", **d))

    return mission_data


player_options = {
    'AP Unlocked Commando': 'GD_DefaultProfiles.Soldier.Profile_Soldier',
    'AP Unlocked Assassin': 'GD_DefaultProfiles.Assassin.Profile_Assassin',
    'AP Unlocked Siren': 'GD_DefaultProfiles.Siren.Profile_Siren',
    'AP Unlocked Gunzerker': 'GD_DefaultProfiles.Mercenary.Profile_Mercenary',
    'AP Unlocked Mechromancer': 'GD_TulipPackageDef.Profiles.Profile_Mechromancer',
    'AP Unlocked Psycho': 'GD_LilacPackageDef.Profiles.Profile_LilacPlayerClass',
}

@hook("WillowGame.WillowGFxLobbyLoadCharacter:SavesUpdated", Type.POST)
def populate_character_select_menu(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    # TODO: if get_globals().settings.get("fully_unlocked_mode") == 1:
    for player_name in player_options:
        obj.DisplayedCharacterDataList.append(unrealsdk.make_struct("LoadCharacterData", 
            SaveDataId=-1,
            CharClass=player_name,
        ))
    obj.DisplayedCharacterDataList.append(unrealsdk.make_struct("LoadCharacterData", 
        SaveDataId=-1,
        CharClass="AP Unlocked Random Class",
    ))

@hook("WillowGame.WillowGFxLobbyLoadCharacter:OnSlotClicked")
def on_select_character_option(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    idx = obj.TopSlotDataIndex + args.SlotIndex
    clicked_entry = obj.DisplayedCharacterDataList[idx]
    if clicked_entry.SaveDataId != -1: # -1 is "create character"
        return
    if not clicked_entry.CharClass.startswith("AP "):
        return

    if clicked_entry.CharClass == "AP Unlocked Random Class":
        template_name = random.choice(list(player_options.values()))
    else:
        template_name = player_options[clicked_entry.CharClass]

    template_save_game = unrealsdk.find_object('PlayerSaveGame', template_name)
    new_save_game = unrealsdk.construct_object('PlayerSaveGame', template_save_game, template_obj=template_save_game)
    new_save_game.MissionPlaythroughs[0].MissionData = construct_mission_data()
    # new_save_game.MissionPlaythroughs[0].MissionData = construct_mission_data()
    # new_save_game.PlotMissionNumber = 3
    # new_save_game.LastVisitedTeleporter = "WaterfrontToGlacial"
    
    get_pc().GetWillowGlobals().GetWillowSaveGameManager().SetCachedPlayerSaveGame(0, new_save_game)
    get_pc().LoadCachedSaveGame()

    # get_pc().openlArg("SouthernShelf_P")
    get_pc().openlArg("Glacial_P")
    return Block

# TODO: switch to add/remove hooks during init_data based on settings
@hook("WillowGame.WillowPlayerController:TryPromptForFastForward")
def block_fast_forward(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if get_globals().settings.get("fully_unlocked_mode") == 1:
        return Block

@hook("WillowGame.MarketingUnlockInventoryDefinition:GenerateUnlockedItems")
def block_start_items(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if get_globals().settings.get("delete_starting_gear") == 1:
        return Block

@hook("WillowGame.StatusMenuExGFxMovie:DisplayMarketingUnlockDialogIfNecessary")
def block_start_dialogs(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if get_globals().settings.get("fully_unlocked_mode") == 1:
        return Block

@hook('WillowGame.WillowPlayerController:ServerShowChapterHeader')
def block_chapter_header(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if get_globals().settings.get("fully_unlocked_mode") == 1:
        return Block


@hook("WillowGame.WillowInteractiveObject:UseObject")
def use_sanct_bounty_board(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    if obj.PathName(obj) != "SanctuaryAir_Dynamic.TheWorld:PersistentLevel.WillowInteractiveObject_8":
        return
    if get_globals().settings.get("fully_unlocked_mode", 0) == 0:
        return

    pc = get_pc()
    try:
        # impossible to talk to brick for bearer of bad news 
        pc.WorldInfo.GRI.MissionTracker.UpdateObjective(unrealsdk.find_object("MissionObjectiveDefinition", "GD_Z1_BearerBadNews.M_BearerBadNews:TalkBrick"))
        # talk to roland
        pc.WorldInfo.GRI.MissionTracker.UpdateObjective(unrealsdk.find_object("MissionObjectiveDefinition", "GD_Episode07.M_Ep7_ATrainToCatch:HeadBackToSanctuary"))
        # grab note
        pc.WorldInfo.GRI.MissionTracker.UpdateObjective(unrealsdk.find_object("MissionObjectiveDefinition", "GD_Episode11.M_Ep11_LikeATonOf:GrabNote"))
        
        
    except Exception as e:
        print(e)
        pass

character_hooks = []

if game_is_bl2():
    character_hooks = [
        populate_character_select_menu,
        on_select_character_option,
        block_fast_forward,
        block_start_items,
        block_start_dialogs,
        use_sanct_bounty_board,
        block_chapter_header,
    ]

