import unrealsdk
from mods_base import get_pc
from coroutines import start_coroutine_tick, WaitForSeconds


def init_traps(): 
    try:
        unrealsdk.load_package("InnerCore_combat00")
        keep_alive(unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Population_Eridian_Opha.Population.PopDef_Opha_Normal.PopulationFactoryBalancedAIPawn_9"))
        unrealsdk.load_package("GD_Prototype_Streaming_SF")
        keep_alive(unrealsdk.find_object("SkillDefinition", "GD_Prototype_ActionSkill.ActionPackages.ActionPackage_RubberMode"))
        keep_alive(unrealsdk.find_object("SkillDefinition", "GD_Prototype_Skills_GBX.ActionPackages.ActionPackage_ClapInTheBox"))
        keep_alive(unrealsdk.find_object("SkillDefinition", "GD_Prototype_Skills_GBX.ActionPackages.ActionPackage_ClapInTheBox_CountKills"))
        return True
    except:
        return False

def keep_alive(obj) -> None:
    obj.ObjectFlags |= 0x4000
    return

trap_pawn_def = ()

def get_game_spawn_trap(spawn_name):
    if spawn_name == "Opha":
        return [
            {
                "ai_pawn": "GD_Population_Eridian_Opha.Population.PopDef_Opha_Normal.PopulationFactoryBalancedAIPawn_9", "dists": [1000, -1000]
            }
        ]
def trigger_game_trap(trap_name):
    pc = get_pc()
    if trap_name == "Not Now, Claptrap!":
        start_coroutine_tick(trigger_fragtrap_skill(unrealsdk.find_object("SkillDefinition", "GD_Prototype_ActionSkill.ActionPackages.ActionPackage_RubberMode"), 20))
        return True
    elif trap_name == "Not Helping Claptrap!":
        start_coroutine_tick(lambda : 
                             trigger_fragtrap_skill(unrealsdk.find_object("SkillDefinition", "GD_Prototype_Skills_GBX.ActionPackages.ActionPackage_ClapInTheBox"), 20),
                             pc.Behavior_ActivateSkill(unrealsdk.find_object("SkillDefinition", "GD_Prototype_Skills_GBX.ActionPackages.ActionPackage_ClapInTheBox_CountKills"))
                             )
        return True
    elif trap_name == "Fling": #fling player in a random direction
        pass
    elif trap_name == "Leaky Wallet": #periodicly leak moonstone / money
        pass
        
def trigger_fragtrap_skill(skill, duration):
    pc = get_pc()
    ui  = unrealsdk.find_all("WillowHUDGFxMovie")[-1]
    constraints = skill.SkillConstraints
    skill.SkillConstraints = [] #remove constraints, to allow triggering subroutine with mis matching conditions
    pc.Behavior_ActivateSkill(skill, None, 5)
    skill.SkillConstraints = constraints
    ui.ClientHudClapTrappedAlertIntro(skill, 7, 4)
    yield WaitForSeconds(duration)
    ui.ClientHudClapTrappedAlertOutro()
    return None