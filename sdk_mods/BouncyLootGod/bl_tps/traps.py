import unrealsdk
from mods_base import get_pc
from coroutines import start_coroutine_tick, WaitForSeconds


def init_traps(): 
    try:
        unrealsdk.load_package("InnerCore_combat00")
        keep_alive(unrealsdk.find_object("PopulationFactoryBalancedAIPawn", "GD_Population_Eridian_Opha.Population.PopDef_Opha_Normal.PopulationFactoryBalancedAIPawn_9"))
        unrealsdk.load_package("GD_Prototype_Streaming_SF")
        keep_alive(unrealsdk.find_object("SkillDefinition", "GD_Prototype_ActionSkill.ActionPackages.ActionPackage_RubberMode"))
        keep_alive(unrealsdk.find_object("SkillDefinition", "GD_Prototype_ActionSkill.ActionPackages.ActionPackage_ClapInTheBox"))
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
    if trap_name == "Not Helping Claptrap!":
        start_coroutine_tick(trigger_fragtrap_skill(unrealsdk.find_object("SkillDefinition", "GD_Prototype_ActionSkill.ActionPackages.ActionPackage_ClapInTheBox"), 20))
        return True
    elif trap_name == "Not Now Claptrap!":
        start_coroutine_tick(lambda : 
                             trigger_fragtrap_skill(unrealsdk.find_object("SkillDefinition", "GD_Prototype_ActionSkill.ActionPackages.ActionPackage_RubberMode"), 20),
                             pc.Behavior_ActivateSkill(unrealsdk.find_object("SkillDefinition", "GD_Prototype_ActionSkill.ActionPackages.ActionPackage_RubberMode_CountKills"))
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
    ui.FragTrapProgramIntro(skill, 7, 4)
    ui_value = duration
    yield WaitForSeconds(3.1) #analyser overlay duration-ish
    tick_size = 0.5
    while ui_value >= 0:
        yield WaitForSeconds(tick_size)
        ui.FragTrapProgramUpdate(1 - (ui_value / duration))
        ui_value = ui_value - tick_size
    ui.FragTrapProgramOutro()
    return None