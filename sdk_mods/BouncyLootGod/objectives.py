import unrealsdk
import unrealsdk.unreal as unreal
from mods_base import hook, Game
from unrealsdk.hooks import Type
from BouncyLootGod.state import get_globals

from BouncyLootGod.archi_data import loc_name_to_id

from BouncyLootGod.networking import push_locations

objective_pn_to_loc_name = {
    "GD_Episode10.M_Ep10_BirdISTheWord:GetClaptrapUpgrade": "Enemy: Bloodwing",
    "GD_Orchid_Plot_Mission09.M_Orchid_PlotMission09:KillBossWorm": "Enemy: The Leviathan",
    "GD_Orchid_SM_EndGameClone.M_Orchid_EndGame:KillBossWorm": "Enemy: The Leviathan",
    "GD_Co_Chapter01.M_CH01b_MoonShot:KillThatAsshole": "Enemy: That Asshole",
    "GD_Cork_DahlFactory_Plot.M_Cork_DahlFactory_Plot:KillBoss": "Enemy: Felicity Rampant",
    # "GD_Co_Chapter11.M_DahlDigsite:DefeatRk5_Objective": "Enemy: Raum-Kampfjet Mark V", #it is not updated after defeating rk5.
    "GD_Co_Chapter11.M_DahlDigsite:DefeatVaultBossStageTwo": "Enemy: The Empyrean Sentinel",
    "GD_Co_CorkRaid.M_CorkRaid:DefeatTheRaidGuardianPlus": "Enemy: The Invincible Empyrean Sentinel",
    "GD_Ma_Chapter06.M_Ma_Chapter06:01_Kill_Shadowtrap": "Enemy: EOS",
}

@hook("WillowGame.MissionTracker:UpdateObjective", Type.POST)
def update_objective(obj: unreal.UObject, args: unreal.WrappedStruct, ret, func: unreal.BoundFunction):
    pn = args.MissionObjective.PathName(args.MissionObjective)
    loc_name = objective_pn_to_loc_name.get(pn)
    if not loc_name:
        return

    loc_id = loc_name_to_id.get(loc_name)
    if loc_id is None:
        return

    blg = get_globals()
    if loc_id not in blg.locations_checked and loc_id not in blg.locs_to_send:
        blg.locs_to_send.append(loc_id)
        push_locations()
