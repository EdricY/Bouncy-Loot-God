import unrealsdk
from mods_base import get_pc
from coroutines import start_coroutine_tick, WaitForSeconds

def wait_for(seconds, func):
    yield WaitForSeconds(seconds)
    func()
def display_claptrapped_ui(title= "You've been Archipelago'd!", skill=None,duration_override=None, skill_name_override=None):
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
    hud_movie.Claptrapped_Text = title
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