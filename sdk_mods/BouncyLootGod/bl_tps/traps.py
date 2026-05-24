import unrealsdk
import random
import math
from mods_base import get_pc
from coroutines import start_coroutine_tick, WaitForSeconds
from BouncyLootGod.loot_pools import spawn_gear_from_pool, create_modified_item_pool


def init_game_traps(): 
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
        display_claptrapped_ui(duration_override=3, skill_name_override="Spawn Trap: " + spawn_name)
        return [
            {
                "ai_pawn": "GD_Population_Eridian_Opha.Population.PopDef_Opha_Normal.PopulationFactoryBalancedAIPawn_9", "dists": [1000, -1000]
            }
        ]
def trigger_game_trap(trap_name):
    pc = get_pc()
    if trap_name == "Rubber Ducky":
        start_coroutine_tick(trigger_fragtrap_skill(unrealsdk.find_object("SkillDefinition", "GD_Prototype_ActionSkill.ActionPackages.ActionPackage_RubberMode")))
        return True
    elif trap_name == "Clap-in-a-Box":
        start_coroutine_tick(trigger_fragtrap_skill(
            unrealsdk.find_object("SkillDefinition", "GD_Prototype_Skills_GBX.ActionPackages.ActionPackage_ClapInTheBox"), 
            unrealsdk.find_object("SkillDefinition", "GD_Prototype_Skills_GBX.ActionPackages.ActionPackage_ClapInTheBox_CountKills"),
            duration_override=6
            )
         )
        return True

    elif trap_name == "Slippery": #just drop current weapon
        display_claptrapped_ui(duration_override=1.2, skill_name_override=trap_name)
        pc = get_pc()
        pc.ServerThrowPawnActiveWeapon()
    elif trap_name == "Item Explosion": #throw all items in backpack.
        display_claptrapped_ui(duration_override=1.2, skill_name_override=trap_name)
        pc = get_pc()
        im = pc.GetPawnInventoryManager()
        backpack = im.Backpack[:]
        for item in backpack:
            pc.ServerThrowInventory(item, 1)
        im.Backpack = []
        #this is needed as the game does not update the internal counter, 
        # leading to "full backpack" error with available slots when trying to pick up items
        im.ServerUpdateBackpackInventoryCount(0)
    elif trap_name == "Fling": #fling player in a random direction
        pawn = get_pc().Pawn
        display_claptrapped_ui(duration_override=1.2, skill_name_override=trap_name)
        pawn.DoJump(0)
        radius = 4500 #yeetus deletus
        vertical = 2000 #yeetus deletus
        angle = random.random() * math.pi * 2
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        pawn.Velocity = unrealsdk.make_struct("Vector", X=x, Y=y, Z=vertical)
    elif trap_name == "Leaky Wallet": #periodicly leak moonstone / money
        start_coroutine_tick(drop_moonstone_cluster(0.6, 0.5))
    return False
def drop_moonstone_cluster(percentage_to_drop, tick_rate, max_duration=30):
    pc = get_pc()
    dropped = 0
    moonstone = pc.PlayerReplicationInfo.Currency[1]
    max_to_drop = moonstone.CurrentAmount * percentage_to_drop
    duration = 0
    display_claptrapped_ui(skill_name_override="Leaky Wallet")
    while dropped <= max_to_drop and duration < max_duration:
        yield WaitForSeconds(tick_rate)
        print("Dropping moonstones")
        (item_pool, cleanup_funcs) = create_modified_item_pool("BLGMoonstonePool",inv_bal_def_names=["GD_ItemGrades.Currency.ItemGrade_Currency_Moonstone_Cluster"])
        spawn_gear_from_pool(item_pool, -150, 0, cleanup_funcs=cleanup_funcs, override_loc=None) #spawn behind
        pc.PlayerReplicationInfo.AddCurrencyOnHand(1, -4)
        dropped += 4
        duration += tick_rate
    pc.ClientHudClapTrappedAlertOutro()
    return None
def wait_for(seconds, func):
    yield WaitForSeconds(seconds)
    func()
def display_claptrapped_ui(skill=None,duration_override=None, skill_name_override=None):
    pc = get_pc()
    print(str(skill) + ", " + str(duration_override) + ", " + str(skill_name_override))
    if not skill:
        try:
            skill = unrealsdk.find_object("SkillDefinition", "GD_Cork_Weap_Lasers.Skills.Skill_LightSaberDeflection")
        except:
            pass
    duration_backup = None
    print(str(skill) + ", " + str(duration_override) + ", " + str(skill_name_override))
    name_backup = None
    if skill and duration_override:
        duration_backup = skill.InitialDuration
        skill.InitialDuration = duration_override
    if skill and skill_name_override:
        name_backup = skill.SkillName
        skill.SkillName = skill_name_override
    hud_movie = pc.GetHudMovie()
    org = hud_movie.Claptrapped_Text
    hud_movie.Claptrapped_Text = "You've been Archipelago'd!"
    pc.ClientHudClapTrappedAlertIntro(skill)
    if skill and skill_name_override:
        skill.SkillName = name_backup
    hud_movie.Claptrapped_Text = org
    if duration_override is not None:
        if skill:
            skill.InitialDuration = duration_backup
        start_coroutine_tick(wait_for(duration_override, lambda: pc.ClientHudClapTrappedAlertOutro()))
        # yield WaitForSeconds(duration_override)
    # return None
def trigger_fragtrap_skill(skill, after_duration_skill=None, duration_override=None, name_override=None):
    print("Starting "+ str(skill))
    pc = get_pc()
    initial_duration = skill.InitialDuration
    if duration_override is not None:
        skill.InitialDuration = duration_override
    constraints = skill.SkillConstraints
    skill.SkillConstraints = [] #remove constraints, to allow triggering subroutine with mis matching conditions
    pc.ServerActivateSkill(skill, None, 5)
    skill.SkillConstraints = constraints
    skill_name = skill.SkillName
    if name_override is not None:
        skill.SkillName = name_override
    display_claptrapped_ui(skill)
    if name_override is not None:
        skill.SkillName = skill_name
    if duration_override is not None:
        skill.InitialDuration = initial_duration
    yield WaitForSeconds(duration_override or skill.InitialDuration)
    pc.ClientHudClapTrappedAlertOutro()
    print("Finishing "+ str(skill))
    if after_duration_skill:
        pc.ServerDeactivateSkill(skill, True)
        pc.ServerActivateSkill(after_duration_skill, None, 5)
    return None