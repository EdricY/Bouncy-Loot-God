import unrealsdk
import unrealsdk.unreal as unreal
from unrealsdk.hooks import Type, Block
import random
from mods_base import get_pc, ObjectFlags
from BouncyLootGod.oob import get_loc_in_front_of_player
from BouncyLootGod.state import get_globals, get_or_create_package
from BouncyLootGod.archi_data import item_name_to_id, loc_name_to_id
from BouncyLootGod.bl_tps.ui import display_claptrapped_ui

# some things here adapted from RoguelandsGamemode/Looties.py

# orange = unrealsdk.make_struct("Color", R=128, G=64, B=0, A=255)

def pathname(obj):
    if obj is None:
        return None
    return obj.PathName(obj)

# unused, maybe useful
def override_hook_once(hook, value):
    """override only the next call of the given hook to return the given value."""
    def override_func(self, caller: unreal.UObject, function: unreal.UFunction, params: unreal.WrappedStruct):
        unrealsdk.hooks.remove_hook(hook, Type.PRE, "override_hook_once")
        return Block, value
    unrealsdk.hooks.add_hook(hook, Type.PRE, "override_hook_once", override_func)

# new approach... don't clone balance defs, modify and return cleanup functions
def modify_inv_bal_def(
    inv_bal_def,
    relic_rarity="",
    skip_alien=False,
):
    my_cleanup_funcs = []
    m_backup = []
    for m in inv_bal_def.Manufacturers: # restricted manufacturers
        for g in m.Grades:
            m_backup.append(g.GameStageRequirement.MinGameStage)
            g.GameStageRequirement.MinGameStage = 0
    def reset_manufacturers(inv_bal_def, m_backup):
        for m in inv_bal_def.Manufacturers:
            for g in m.Grades:
                g.GameStageRequirement.MinGameStage = m_backup.pop(0)
    r_m_func = lambda inv_bal_def=inv_bal_def, m_backup=m_backup: reset_manufacturers(inv_bal_def, m_backup)
    my_cleanup_funcs.append(r_m_func)

    if (plc := inv_bal_def.PartListCollection):
        bd_backup = []
        for wp in plc.DeltaPartData.WeightedParts: # grenade elements
            bd_backup.append(wp.MinGameStageIndex)
            wp.MinGameStageIndex = 0
        for wp in plc.BetaPartData.WeightedParts: # grenade delivery
            bd_backup.append(wp.MinGameStageIndex)
            wp.MinGameStageIndex = 0
        def reset_bd(inv_bal_def, bd_backup):
            plc = inv_bal_def.PartListCollection
            for wp in plc.DeltaPartData.WeightedParts:
                wp.MinGameStageIndex = bd_backup.pop(0)
            for wp in plc.BetaPartData.WeightedParts:
                wp.MinGameStageIndex = bd_backup.pop(0)
        r_bd_func = lambda inv_bal_def=inv_bal_def, bd_backup=bd_backup: reset_bd(inv_bal_def, bd_backup)
        my_cleanup_funcs.append(r_bd_func)

        if relic_rarity:
            th_backup = []
            for idx in range(len(plc.ThetaPartData.WeightedParts)): # relic grade
                wp = plc.ThetaPartData.WeightedParts[idx]
                th_backup.append(wp.DefaultWeightIndex)
                if wp.Part and not wp.Part.Rarity.BaseValueAttribute.Name.endswith("_" + relic_rarity):
                    wp.DefaultWeightIndex = 7
            def reset_theta(inv_bal_def, th_backup):
                plc = inv_bal_def.PartListCollection
                for wp in plc.ThetaPartData.WeightedParts:
                    wp.DefaultWeightIndex = th_backup.pop(0)
            r_th_func = lambda inv_bal_def=inv_bal_def, th_backup=th_backup: reset_theta(inv_bal_def, th_backup)
            my_cleanup_funcs.append(r_th_func)

    if inv_bal_def.Class.Name == "":
        rplc = inv_bal_def.RuntimePartListCollection
        el_backup = []
        for wp in rplc.ElementalPartData.WeightedParts: # gun elements
            el_backup.append(wp.MinGameStageIndex)
            wp.MinGameStageIndex = 0
        def reset_el(inv_bal_def, el_backup):
            rplc = inv_bal_def.RuntimePartListCollection
            for wp in rplc.ElementalPartData.WeightedParts:
                wp.MinGameStageIndex = el_backup.pop(0)
        r_el_func = lambda inv_bal_def=inv_bal_def, el_backup=el_backup: reset_el(inv_bal_def, el_backup)
        my_cleanup_funcs.append(r_el_func)

        if skip_alien and len(rplc.BarrelPartData.WeightedParts):
            barrel_backup = []
            for wp in rplc.BarrelPartData.WeightedParts: # remove e-tech elements
                if wp.Part is None:
                    barrel_backup.append(wp.Part)
                elif "Alien" in wp.Part.Name:
                    barrel_backup.append(wp.Part)
                    wp.Part = None
            def reset_barrel(inv_bal_def, barrel_backup):
                rplc = inv_bal_def.RuntimePartListCollection
                for wp in rplc.BarrelPartData.WeightedParts:
                    if wp.Part is None:
                        wp.Part = barrel_backup.pop(0)
            r_barrel_func = lambda inv_bal_def=inv_bal_def, barrel_backup=barrel_backup: reset_barrel(inv_bal_def, barrel_backup)
            my_cleanup_funcs.append(r_barrel_func)

    return my_cleanup_funcs


def create_modified_item_pool(
    name="BLG_itempool",
    base_pool=None,
    pool_names=[],
    inv_bal_def_names=[],
    package_name="BouncyLootGod",
    relic_rarity="",
    skip_alien=False,
    uniform_probability=True,
):
    package = get_or_create_package(package_name)
    if base_pool is None:
        item_pool = unrealsdk.construct_object("ItemPoolDefinition", package, name)
    elif type(base_pool) is str:
        base_pool = unrealsdk.find_object("ItemPoolDefinition", base_pool)
        item_pool = unrealsdk.construct_object("ItemPoolDefinition", package, base_pool.Name, 0, base_pool)
    else:
        item_pool = unrealsdk.construct_object("ItemPoolDefinition", package, base_pool.Name, 0, base_pool)

    item_pool.MinGameStageRequirement = None
    probability = unrealsdk.make_struct("AttributeInitializationData", BaseValueConstant=1, BaseValueScaleConstant=1)
    my_cleanup_funcs = []

    # modify existing balanced items (if base pool)
    for bi in item_pool.BalancedItems:
        if (sub_pool := bi.ItmPoolDefinition):
            (new_sub_pool, p_cleanup_funcs) = create_modified_item_pool(base_pool=sub_pool, relic_rarity=relic_rarity, skip_alien=skip_alien, package_name=package_name, uniform_probability=uniform_probability)
            bi.ItmPoolDefinition = new_sub_pool
            my_cleanup_funcs.extend(p_cleanup_funcs)
        elif (inv_bal_def := bi.InvBalanceDefinition):
            i_cleanup_funcs = modify_inv_bal_def(inv_bal_def, relic_rarity=relic_rarity, skip_alien=skip_alien)
            my_cleanup_funcs.extend(i_cleanup_funcs)
        if uniform_probability:
            bi.Probability = probability

        if skip_alien and inv_bal_def and "Alien" in inv_bal_def.Name:
            bi.Probability = unrealsdk.make_struct("AttributeInitializationData", BaseValueConstant=0, BaseValueScaleConstant=1)

    # add ibds from params
    for inv_bal_def_name in inv_bal_def_names:
        try:
            inv_bal_def = unrealsdk.find_object("InventoryBalanceDefinition", inv_bal_def_name)
            i_cleanup_funcs = modify_inv_bal_def(inv_bal_def, relic_rarity=relic_rarity, skip_alien=skip_alien)
            my_cleanup_funcs.extend(i_cleanup_funcs)
            balanced_item = unrealsdk.make_struct("BalancedInventoryData", InvBalanceDefinition=inv_bal_def, Probability=probability, bDropOnDeath=True)
            item_pool.BalancedItems.append(balanced_item)
        except ValueError:
            print("failed to load: " + inv_bal_def_name)

    # add pools from params
    for pool_name in pool_names:
        sub_pool = unrealsdk.find_object("ItemPoolDefinition", pool_name)
        (new_sub_pool, p_cleanup_funcs) = create_modified_item_pool(base_pool=sub_pool, relic_rarity=relic_rarity, skip_alien=skip_alien, package_name=package_name, uniform_probability=uniform_probability)
        balanced_item = unrealsdk.make_struct("BalancedInventoryData", ItmPoolDefinition=new_sub_pool, Probability=probability, bDropOnDeath=True)
        item_pool.BalancedItems.append(balanced_item)
        my_cleanup_funcs.extend(p_cleanup_funcs)

    return (item_pool, my_cleanup_funcs)


unique_shield_def_names = [
    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_Haymaker',
    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_DeadlyBloom',
    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_AsteroidBelt',
    'GD_Ma_Shields.A_Item_Unique.ItemGrade_Gear_Shield_Juggernaut_03_ShieldOfAges',
    'GD_Ma_Shields.A_Item_Unique.ItemGrade_Gear_Shield_Naught',
    'GD_Cork_Shields.A_Item_Custom.ItemGrade_Shield_RapidRelease',
    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Starburst',
    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_MoxxisSlammer'
]

unique_grenade_def_names = [
    'GD_Ma_GrenadeMods.A_Item_Unique.GM_DataScrubber',
    'GD_GrenadeMods.A_Item_Custom.GM_BabyBoomer',
    'GD_GrenadeMods.A_Item_Custom.GM_SkyRocket',
    'GD_GrenadeMods.A_Item_Custom.GM_Snowball',
    'GD_Cork_GrenadeMods.A_Item_Custom.GM_KissOfDeath',
    'GD_Cork_GrenadeMods.A_Item_Custom.GM_MonsterTrap'
]

unique_ozkit_def_names = [
    # "GD_MoonItems.A_Item_Unique.A_AckAck", #legendary
    # "GD_MoonItems.A_Item_Unique.A_Astrotech", #legendary, 3dd1.e
    "GD_MoonItems.A_Item_Unique.A_Oxidizer",
    # "GD_MoonItems.A_Item_Unique.A_SupportRelay", #legendary
    "GD_MoonItems.A_Item_Unique.A_Poopdeck",
    # "GD_MoonItems.A_Item_Unique.MoonItem_Springs", #starter white oz kit
    "GD_MoonItems.A_Item_Unique.A_Freedom",
    "GD_MoonItems.A_Item_Unique.A_Invigoration",
    "GD_MoonItems.A_Item_Unique.A_SystemsPurge",
    # "GD_MoonItems.A_Item_Unique.A_MoonlightSaga", #legendary
    "GD_Pet_MoonItems.A_Item_Unique.A_AntiAir_PerdyLights",
]
# future_reference = {
#     "HealingInstant": "GD_ItemGrades.BuffDrink.ItemGrade_BuffDrink_HealingInstant",
#     "HealingRegen": "GD_ItemGrades.BuffDrink.ItemGrade_BuffDrink_HealingRegen",
#     "OxygenInstant": "GD_ItemGrades.BuffDrink.ItemGrade_BuffDrink_OxygenInstant",
#     "Toughness": "GD_ItemGrades.BuffDrink.ItemGrade_BuffDrink_Toughness",
# }
individual_receivables_dict = {
    "Bad Touch": "GD_Cork_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch",
    "Cyber Eagle": "GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_CyberColt",
    "Ack Ack": "GD_MoonItems.A_Item_Unique.A_AckAck",
    "3DD1.E": "GD_MoonItems.A_Item_Unique.A_Astrotech",
    "Freedom": "GD_MoonItems.A_Item_Unique.A_Freedom",
    "Invigoration": "GD_MoonItems.A_Item_Unique.A_Invigoration",
    "Moonlight Saga": "GD_MoonItems.A_Item_Unique.A_MoonlightSaga",
    "Oxidizer": "GD_MoonItems.A_Item_Unique.A_Oxidizer",
    "Cathartic": "GD_MoonItems.A_Item_Unique.A_Poopdeck",
    "Springs' Oz Kit": "GD_MoonItems.A_Item_Unique.A_Springs",
    "Support Relay": "GD_MoonItems.A_Item_Unique.A_SupportRelay",
    "Systems Purge": "GD_MoonItems.A_Item_Unique.A_SystemsPurge",
    "Bullpup": "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Old_Hyperion_3_Bullpup",
    "Smasher": "GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Smasher",
    "Gwens Other Head": "GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_GwensOtherHead",
    "Good Touch": "GD_Cork_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_GoodTouch",
    "Ice Scream": "gd_cork_weap_assaultrifle.A_Weapons_Unique.AR_Vladof_3_IceScream",
    "Wallop": "gd_cork_weap_assaultrifle.A_Weapons_Unique.AR_Jakobs_3_Wallop",
    "Hail": "gd_cork_weap_assaultrifle.A_Weapons_Unique.AR_Vladof_3_Hail",
    "Ol' Painful": "gd_cork_weap_assaultrifle.A_Weapons_Unique.AR_Vladof_3_OldPainful",
    "Mining Laser": "GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Hyperion_3_Mining",
    "Firestarta": "GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Dahl_3_Firestarta",
    "Freezeeasy": "GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Maliwan_3_Blizzard", #
    "Vibra Pulse": "GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Maliwan_3_VibraPulse",
    "Toby's Bright Spadroon": "GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Maliwan_4_SavorySideSaber",
    "Vandergraffen": "GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Tediore_3_Vandergraffen",
    "Ol' Rosie": "GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Maliwan_4_Rosie",
    "E-Gun": "GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Maliwan_4_Egun",
    "Volt Thrower": "GD_Cork_Weap_Launchers.A_Weapons_Unique.RL_Tediore_3_Rocketeer",
    "Creamer": "GD_Cork_Weap_Launchers.A_Weapons_Unique.RL_Torgue_3_Creamer",
    "Globber": "GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Globber",
    "Fibber": "GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Fibber",
    "Moonface": "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_Moonface",
    "Boganella": "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Boganella",
    "Heart Breaker": "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_HeartBreaker",
    "Octo": "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Octo",
    "Wombat": "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_Wombat",
    "Too Scoops": "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_TooScoops",
    "Boomacorn": "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_Boomacorn",
    "Jack-O'-Cannon": "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_JackOCannon",
    "Mareks Mouth": "GD_Cork_Weap_SMG.A_Weapons_Unique.SMG_Bandit_3_MareksMouth",
    "Meat Grinder": "GD_Cork_Weap_SMG.A_Weapons_Unique.SMG_Bandit_3_MeatGrinder",
    "Fridgia": "GD_Weap_SMG.A_Weapons_Unique.SMG_Dahl_3_Fridgia",
    "Frostfire": "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_Frostfire",
    "Black Snake": "GD_Cork_Weap_SMG.A_Weapons_Unique.SMG_Old_Hyperion_BlackSnake",
    "Wet Week": "GD_Cork_Weap_SniperRifles.A_Weapons_Unique.Sniper_Dahl_3_WetWeek",
    "Fremington's Edge": "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_FremingtonsEdge",
    "Razorback": "GD_Cork_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Razorback",
    "Chère-amie": "GD_Cork_Weap_SniperRifles.A_Weapons_Unique.Sniper_Maliwan_3_ChereAmie",
    "The Machine": "GD_Cork_Weap_SniperRifles.A_Weapons_Unique.Sniper_Vladof_3_TheMachine",
    "Lady Fist": "GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_LadyFist",
    # "GBX": "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_1_GBX",#
    # "1": "GD_Weap_SMG.A_Weapons_Unique.SMG_Gearbox_1",#
    # "1": "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Gearbox_1",#
    "Torguemada": "GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_Torguemada",
    "Moxxi's Probe": "GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Maliwan_3_Moxxis_Probe",
    "Boss Nova": "GD_Cypressure_Weapons.A_Weapons_Unique.AR_Bandit_3_BossNova",
    "Tannis' Laser of Enlightenment": "GD_Ma_Weapons.A_Weapons_Unique.Laser_Maliwan_3_Enlightenment",
    "Minac's Atonement": "GD_Ma_Weapons.A_Weapons_Unique.Laser_Maliwan_3_Minac",
    "Party Popper": "GD_Ma_Weapons.A_Weapons_Unique.Pistol_Bandit_3_PartyPopper",
    "Hard Reboot": "GD_Ma_Weapons.A_Weapons_Unique.Pistol_Maliwan_3_HardReboot",
    "Company Man": "GD_Cypressure_Weapons.A_Weapons_Unique.SG_Hyperion_3_CompanyMan",
    "Moonscaper": "GD_Cypressure_Weapons.A_Weapons_Unique.SG_Torgue_3_Landscaper2",
    "Fast Talker": "GD_Cypressure_Weapons.A_Weapons_Unique.SMG_Bandit_3_FastTalker",
    "Shield Of Ages": "GD_Ma_Shields.A_Item_Unique.ItemGrade_Gear_Shield_Juggernaut_03_ShieldOfAges",
    "Naught": "GD_Ma_Shields.A_Item_Unique.ItemGrade_Gear_Shield_Naught",
    "Heartfull Splodger": "GD_Ma_Weapons.A_Weapons_Unique.Laser_Dahl_6_Glitch_HeartfullSplodger",
    "Cutie Killer": "GD_Ma_Weapons.A_Weapons_Unique.SMG_Bandit_6_Glitch_CutieKiller",
    "Perdy Lights": "GD_Pet_MoonItems.A_Item_Unique.A_AntiAir_PerdyLights",
    "Haymaker": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_Haymaker",
    "Deadly Bloom": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_DeadlyBloom",
    "Asteroid Belt": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_AsteroidBelt",
    "Rapid Release": "GD_Cork_Shields.A_Item_Custom.ItemGrade_Shield_RapidRelease",
    "Sunshine": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Starburst",
    "Slammer": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_MoxxisSlammer",
    "Data Scrubber": "GD_Ma_GrenadeMods.A_Item_Unique.GM_DataScrubber",
    "Baby Boomer": "GD_GrenadeMods.A_Item_Custom.GM_BabyBoomer",
    "Contraband Sky Rocket": "GD_GrenadeMods.A_Item_Custom.GM_SkyRocket",
    "Snowball": "GD_GrenadeMods.A_Item_Custom.GM_Snowball",
    "Kiss of Death": "GD_Cork_GrenadeMods.A_Item_Custom.GM_KissOfDeath",
    "Monster Trap": "GD_Cork_GrenadeMods.A_Item_Custom.GM_MonsterTrap",
    "Avalanche": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_Avalanche",
    "Shooting Star": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_ShootingStar",
    "The Sham": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryNormal",
    "Kala": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryShock",
    "Prismatic Bulwark": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_PrismaticBulwark",
    "Black Hole": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Singularity",
    "Supernova": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Supernova",
    "Fabled Tortoise": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_05_Legendary",
    "Reogenator": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_05_Legendary",
    "Whisky Tango Foxtrot": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_05_Legendary",
    "Bigg Thumppr": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_05_Legendary",
    "The Cradle": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_05_Legendary",
    "Flyin' Maiden": "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_05_Legendary",
    #TODO DLC Uniques + legendaries base + dlc
    # "Legendary": "GD_Cork_ItemGrades.ClassMods.BalDef_ClassMod_Enforcer_05_Legendary",
    # "EridianVanquisher": "GD_Cork_ItemGrades.ClassMods.BalDef_ClassMod_Enforcer_06_EridianVanquisher",
    # "Legendary": "GD_Cork_ItemGrades.ClassMods.BalDef_ClassMod_Gladiator_05_Legendary",
    # "EridianVanquisher": "GD_Cork_ItemGrades.ClassMods.BalDef_ClassMod_Gladiator_06_EridianVanquisher",
    # "Legendary": "GD_Cork_ItemGrades.ClassMods.BalDef_ClassMod_Lawbringer_05_Legendary",
    # "EridianVanquisher": "GD_Cork_ItemGrades.ClassMods.BalDef_ClassMod_Lawbringer_06_EridianVanquisher",
    # "Legendary": "GD_Cork_ItemGrades.ClassMods.BalDef_ClassMod_Prototype_05_Legendary",
    # "EridianVanquisher": "GD_Cork_ItemGrades.ClassMods.BalDef_ClassMod_Prototype_06_EridianVanquisher",
    "Bonus Package": "GD_Cork_GrenadeMods.A_Item_Legendary.GM_BonusPackage",
    "Quasar": "GD_Cork_GrenadeMods.A_Item_Legendary.GM_Quasar",
    "Bouncing Bazza": "GD_GrenadeMods.A_Item_Legendary.GM_BouncingBonny",
    "Fire Bee": "GD_GrenadeMods.A_Item_Legendary.GM_FireBee",
    "Four Seasons": "GD_GrenadeMods.A_Item_Legendary.GM_FourSeasons",
    "Leech": "GD_GrenadeMods.A_Item_Legendary.GM_Leech",
    "Nasty Surprise": "GD_GrenadeMods.A_Item_Legendary.GM_NastySurprise",
    "Pandemic": "GD_GrenadeMods.A_Item_Legendary.GM_Pandemic",
    "Rolling Thunder": "GD_GrenadeMods.A_Item_Legendary.GM_RollingThunder",
    "Storm Front": "GD_GrenadeMods.A_Item_Legendary.GM_StormFront",
    "Excalibastard": "GD_Cork_Weap_Lasers.A_Weapons_Legendary.Laser_Old_Hyperion_5_Excalibastard",
    "Longnail": "GD_Cork_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Vladof_5_Longnail",
    "Torrent": "GD_Cork_Weap_SMG.A_Weapons_Legendary.SMG_Dahl_5_Torrent",
    "Striker": "GD_Cork_Weap_Shotgun.A_Weapons_Legendary.SG_Jakobs_5_Striker",
    "KerBoom": "gd_cork_weap_assaultrifle.A_Weapons_Legendary.AR_Torgue_5_KerBoom",
    "Cryophobia": "GD_Cork_Weap_Launchers.A_Weapons_Legendary.RL_Maliwan_5_Cryophobia",
    "The ZX-1": "GD_Cork_Weap_Lasers.A_Weapons_Legendary.Laser_Dahl_5_ZX1",
    "Fatale": "GD_Cork_Weap_SMG.A_Weapons_Legendary.SMG_Hyperion_5_Bitch",
    "Blowfly": "GD_Cork_Weap_Pistol.A_Weapons_Legendary.Pistol_Dahl_5_Blowfly",
    "Nukem": "GD_Cork_Weap_Launchers.A_Weapons_Legendary.RL_Torgue_5_Nukem",
    "Zim": "GD_Cork_Weap_Pistol.A_Weapons_Legendary.Pistol_Bandit_5_Zim",
    "Hammer Buster II": "gd_cork_weap_assaultrifle.A_Weapons_Legendary.AR_Jakobs_5_HammerBreaker",
    "Skullmasher": "GD_Cork_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Jakobs_5_Skullmasher",
    "Flakker": "GD_Cork_Weap_Shotgun.A_Weapons_Legendary.SG_Torgue_5_Flakker",
    "Invader": "GD_Cork_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Hyperion_5_Invader",
    "Thingy": "GD_Cork_Weap_Launchers.A_Weapons_Legendary.RL_Bandit_5_Thingy",
    "Sledge's Shotty": "GD_Cork_Weap_Shotgun.A_Weapons_Legendary.SG_Bandit_5_SledgesShotgun",
    "IVF": "GD_Cork_Weap_SMG.A_Weapons_Legendary.SMG_Tediore_5_IVF",
    "Shredifier": "gd_cork_weap_assaultrifle.A_Weapons_Legendary.AR_Vladof_5_Shredifier",
    "Major Tom": "gd_cork_weap_assaultrifle.A_Weapons_Legendary.AR_Dahl_5_MajorTom",
    "Min Min Lighter": "GD_Cork_Weap_Lasers.A_Weapons_Legendary.Laser_Tediore_5_Tesla",
    "Cat o' Nine Tails": "GD_Cork_Weap_Lasers.A_Weapons_Legendary.Laser_Dahl_5_Ricochet",
    "Badaboom": "GD_Cork_Weap_Launchers.A_Weapons_Legendary.RL_Bandit_5_BadaBoom",
    "Mongol": "GD_Cork_Weap_Launchers.A_Weapons_Legendary.RL_Vladof_5_Mongol",
    "Shooterang": "GD_Cork_Weap_Pistol.A_Weapons_Legendary.Pistol_Tediore_5_Shooterang",
    "88 Fragnum": "GD_Cork_Weap_Pistol.A_Weapons_Legendary.Pistol_Torgue_5_88Fragnum",
    "Maggie": "GD_Cork_Weap_Pistol.A_Weapons_Legendary.Pistol_Jakobs_5_Maggie",
    "Logan's Gun": "GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Hyperion_5_LogansGun",
    "Viral Marketer": "GD_Cork_Weap_Shotgun.A_Weapons_Legendary.SG_Hyperion_5_ConferenceCall",
    "HellFire": "GD_Cork_Weap_SMG.A_Weapons_Legendary.SMG_Maliwan_5_HellFire",
    "Pitchfork": "GD_Cork_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Dahl_5_Pitchfork",
    "Magma": "GD_Cork_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Maliwan_5_Magma",
    # "Perfect Hibernation": "GD_Cork_Weap_Lasers.A_Weapons_Mission.Laser_Maliwan_PerfectHibernation",
    "Fusillade": "GD_Ma_Weapons.A_Weapons_Legendary.AR_Bandit_5_Fusillade",
    "Longest Yard": "GD_Ma_Weapons.A_Weapons_Legendary.Laser_Hyperion_5_LongestYard",
    "Absolute Zero": "GD_Ma_Weapons.A_Weapons_Legendary.Laser_Maliwan_5_FusionBeam",
    "Thunderfire": "GD_Ma_Weapons.A_Weapons_Legendary.Laser_Maliwan_5_Thunderfire",
    "Laser Disker": "GD_Ma_Weapons.A_Weapons_Legendary.Laser_Tediore_5_LaserDisker",
    "Luck Cannon": "GD_Ma_Weapons.A_Weapons_Legendary.Pistol_Jakobs_5_LuckCannon",
    "Kaneda's Laser": "GD_Ma_Weapons.A_Weapons_Legendary.RL_Tediore_5_KanedasLaser",
    "Cheat Code": "GD_Ma_Weapons.A_Weapons_Legendary.SMG_Hyperion_5_CheatCode",
    "Omni-Cannon": "GD_Ma_Weapons.A_Weapons_Legendary.Sniper_Old_Hyperion_5_OmniCannon",
    "Proletarian Revolution": "GD_Ma_Weapons.A_Weapons_Legendary.Pistol_Vladof_5_Expander",
    "Meganade": "GD_Ma_GrenadeMods.A_Item_Legendary.GM_Meganade",
    "M0RQ": "GD_Ma_Shields.A_Item_Legendary.ItemGrade_Gear_Shield_Chimera_05_M0RQ",
    "Rerouter": "GD_Ma_Shields.A_Item_Legendary.ItemGrade_Gear_Shield_Impact_05_Rerouter",
    "Flayer": "GD_Ma_Weapons.A_Weapons_Legendary.SG_Jakobs_5_Flayer",
    "Berrigan": "GD_Petunia_Weapons.Launchers.RL_Vladof_5_Menace",
    "Cry Baby": "GD_Petunia_Weapons.AssaultRifles.AR_Bandit_3_CryBaby",
    "T4s-R": "GD_Petunia_Weapons.Pistols.Pistol_Hyperion_3_T4sr",
    "Party Line": "GD_Petunia_Weapons.Shotguns.SG_Tediore_3_PartyLine",
    "Boxxy Gunn": "GD_Petunia_Weapons.SMGs.SMG_Tediore_3_Boxxy",
    "Plunkett": "GD_Petunia_Weapons.Snipers.Sniper_Jakobs_3_Plunkett",
}

def get_item_pool_from_gear_kind(gear_kind):
    match gear_kind:
        # Shield
        case "Common Shield":
            return create_modified_item_pool(base_pool="GD_Itempools.ShieldPools.Pool_Shields_All_01_Common")
        case "Uncommon Shield":
            return create_modified_item_pool(base_pool="GD_Itempools.ShieldPools.Pool_Shields_All_02_Uncommon")
        case "Rare Shield":
            return create_modified_item_pool(base_pool="GD_Itempools.ShieldPools.Pool_Shields_All_04_Rare")
        case "VeryRare Shield":
            return create_modified_item_pool(base_pool="GD_Itempools.ShieldPools.Pool_Shields_All_05_VeryRare")
            # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_CrackedSash",

        case "Legendary Shield":
            return create_modified_item_pool("BLGLegendaryShields",
                 base_pool="GD_Itempools.ShieldPools.Pool_Shields_All_06_Legendary",
                 inv_bal_def_names=[
                    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_Avalanche',
                    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_ShootingStar',
                    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_05_Legendary',
                    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryNormal',
                    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryShock',
                    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_PrismaticBulwark',
                    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Singularity',
                    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Supernova',
                    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_05_Legendary',
                    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_05_Legendary',
                    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_05_Legendary',
                    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_05_Legendary',
                    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_05_Legendary',
                    'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_05_Legendary',
            ])
        case "Unique Shield":
            return create_modified_item_pool("BLGUniqueShields",
                inv_bal_def_names=unique_shield_def_names
            )

        # GrenadeMod
        case "Common GrenadeMod":
            return create_modified_item_pool(base_pool="GD_Itempools.GrenadeModPools.Pool_GrenadeMods_01_Common")
        case "Uncommon GrenadeMod":
            return create_modified_item_pool(base_pool="GD_Itempools.GrenadeModPools.Pool_GrenadeMods_02_Uncommon")
        case "Rare GrenadeMod":
            return create_modified_item_pool(base_pool="GD_Itempools.GrenadeModPools.Pool_GrenadeMods_04_Rare")
        case "VeryRare GrenadeMod":
            return create_modified_item_pool(base_pool="GD_Itempools.GrenadeModPools.Pool_GrenadeMods_05_VeryRare")
        case "Legendary GrenadeMod":
            return create_modified_item_pool("BLGLegendaryGrenadeMods", 
                base_pool="GD_Itempools.GrenadeModPools.Pool_GrenadeMods_06_Legendary",
                inv_bal_def_names=[
                    'GD_Cork_GrenadeMods.A_Item_Legendary.GM_BonusPackage',
                    'GD_Cork_GrenadeMods.A_Item_Legendary.GM_Quasar',
                    'GD_GrenadeMods.A_Item_Legendary.GM_BouncingBonny',
                    'GD_GrenadeMods.A_Item_Legendary.GM_FireBee',
                    'GD_GrenadeMods.A_Item_Legendary.GM_FourSeasons',
                    'GD_GrenadeMods.A_Item_Legendary.GM_Leech',
                    'GD_GrenadeMods.A_Item_Legendary.GM_NastySurprise',
                    'GD_GrenadeMods.A_Item_Legendary.GM_Pandemic',
                    'GD_GrenadeMods.A_Item_Legendary.GM_RollingThunder',
                    'GD_GrenadeMods.A_Item_Legendary.GM_StormFront',
                    'GD_Ma_GrenadeMods.A_Item_Legendary.GM_Meganade'
                ]
            )
        case "Unique GrenadeMod":
            return create_modified_item_pool("BLGUniqueGrenadeMods",
                inv_bal_def_names=unique_grenade_def_names
            )

        # ClassMod
        case "Common ClassMod":
            # return (unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.ClassModPools.Pool_ClassMod_01_Common"), [])
            return create_modified_item_pool(base_pool="GD_Itempools.ClassModPools.Pool_ClassMod_01_Common", uniform_probability=False)
        case "Uncommon ClassMod":
            return create_modified_item_pool(base_pool="GD_Itempools.ClassModPools.Pool_ClassMod_02_Uncommon", uniform_probability=False)
        case "Rare ClassMod":
            # TODO: tina classmods rarity ex... GD_Aster_ItemGrades.ClassMods.BalDef_ClassMod_Aster_Assassin > RuntimePartListCollection > AlphaPartData > Rarity > BaseValueAttribute
            return create_modified_item_pool(base_pool="GD_Itempools.ClassModPools.Pool_ClassMod_04_Rare", uniform_probability=False)
        case "VeryRare ClassMod":
            # TODO: tina classmods
            return create_modified_item_pool(base_pool="GD_Itempools.ClassModPools.Pool_ClassMod_05_VeryRare", uniform_probability=False)
        case "Legendary ClassMod":
            return create_modified_item_pool("BLGLegendaryClassMods",
                inv_bal_def_names=[
                    # "GD_Lobelia_ItemGrades.ClassMods.BalDef_ClassMod_Lobelia_Soldier_05_Legendary",
                ],
                pool_names=[
                    'GD_Itempools.ClassModPools.Pool_ClassMod_06_Legendary',
                    'GD_Itempools.ClassModPools.Pool_ClassMod_06_EridianVanquisher',
                    'GD_Pet_ItemPools.ClassModPools.Pool_Chronicler_ClassMod_All'
                    
                ],
            )

        # Relic
        case "Common Oz Kit":
            return create_modified_item_pool("BLGCommonOzKit",
                base_pool="GD_Itempools.MoonItemPools.Pool_MoonItem_01_Common",
                relic_rarity="Common",
            )
        case "Uncommon Oz Kit":
            return create_modified_item_pool("BLGUncommonOzKit",
                base_pool="GD_Itempools.MoonItemPools.Pool_MoonItem_02_Uncommon",
                relic_rarity="Uncommon",
            )
        case "Rare Oz Kit":
            return create_modified_item_pool("BLGRareOzKit",
                base_pool="GD_Itempools.MoonItemPools.Pool_MoonItem_04_Rare",
                relic_rarity="Rare",
            )
        case "VeryRare Oz Kit":
            return create_modified_item_pool("BLGVeryRareOzKit",
                base_pool="GD_Itempools.MoonItemPools.Pool_MoonItem_05_VeryRare",
                relic_rarity="VeryRare",
            )
        case "Legendary Oz Kit":
            return create_modified_item_pool("BLGLegendaryOzKit",
                 base_pool="GD_Itempools.MoonItemPools.Pool_MoonItem_06_Legendary",
                 relic_rarity="Legendary",
             )
        case "Unique Oz Kit":
            return create_modified_item_pool("BLGUniqueOzKit",
                inv_bal_def_names=unique_ozkit_def_names
            )

        # Pistol
        case "Common Pistol":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_01_Common")
        case "Uncommon Pistol":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_02_Uncommon")
        case "Rare Pistol":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_04_Rare")
        case "VeryRare Pistol":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare", skip_alien=True)
        case "Glitch Pistol":
            return create_modified_item_pool(base_pool="GD_Ma_ItemPools.WeaponPools.Pool_Weapons_Pistols_Glitch_Marigold")
        case "Legendary Pistol":
            return create_modified_item_pool("BLGLegendaryPistols",
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_06_Legendary",
                pool_names=[
                    # 'GD_Ma_ItemPools.GrinderPools.CrossDLC_Pool_Weapons_Pistols_06_Legendary',
                    'GD_Ma_ItemPools.WeaponPoolsUnweighted.Pool_Weapons_Pistols_06_Legendary_Unweighted',
                    'GD_Ma_ItemPools.WeaponPools.Pool_Weapons_Pistols_Legendary_Marigold',
                    # 'GD_Pet_ItemPools.GrinderPools.CrossDLC_Pool_Weapons_Pistols_06_Legendary'
                ]
            )
        case "Unique Pistol":
            return create_modified_item_pool("BLGUniquePistols",
                inv_bal_def_names=[
                    "GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_CyberCol"
                    # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_Starter",
                    # 'GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Starter_Vladof_Fragtrap',
                    # 'GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Starter_Maliwan_Athena',
                    # 'GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Starter_Dahl_Wilhelm',
                    # 'GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Starter_Jakobs_Nisha',
                    # 'GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Starter_Hyperion_JackD',
                    # 'GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Starter_Torgue_Anna',
                    'GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Globber',
                    'GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Fibber',
                    'GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_GwensOtherHead',
                    'GD_Ma_Weapons.A_Weapons_Unique.Pistol_Bandit_3_PartyPopper',
                    'GD_Ma_Weapons.A_Weapons_Unique.Pistol_Maliwan_3_HardReboot',
                    'GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_LadyFist',
                    'GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Maliwan_3_Moxxis_Probe',
                    'GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Smasher',
                    'GD_Petunia_Weapons.Pistols.Pistol_Hyperion_3_T4sr'
                ],
                pool_names=[]
            )

        # Shotgun
        case "Common Shotgun":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_01_Common")
        case "Uncommon Shotgun":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_02_Uncommon")
        case "Rare Shotgun":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_04_Rare")
        case "VeryRare Shotgun":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare")
        case "Glitch Shotgun":
            return create_modified_item_pool(base_pool="GD_Ma_ItemPools.WeaponPools.Pool_Weapons_Shotguns_Glitch_Marigold")
        case "Legendary Shotgun":
            return create_modified_item_pool("BLGLegendaryShotguns", 
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_06_Legendary",
                inv_bal_def_names=[
                    # "GD_Anemone_Weapons.Shotgun.Overcompensator.SG_Hyperion_6_Overcompensator"
                ]
            )
        case "Unique Shotgun":
            return create_modified_item_pool("BLGUniqueShotguns",
                inv_bal_def_names=[
                    'GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_Moonface',
                    'GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Boganella',
                    'GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_HeartBreaker',
                    'GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Octo',
                    'GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_Wombat',
                    'GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_TooScoops',
                    'GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_Boomacorn',
                    'GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_JackOCannon',
                    'GD_Cypressure_Weapons.A_Weapons_Unique.SG_Hyperion_3_CompanyMan',
                    'GD_Cypressure_Weapons.A_Weapons_Unique.SG_Torgue_3_Landscaper2',
                    'GD_Petunia_Weapons.Shotguns.SG_Tediore_3_PartyLine',
                    # 'GD_Cork_Weap_Shotgun.A_Weapons_Unique.Shotgun_Starter_Hyperion_Wilhelm',
                    # 'GD_Cork_Weap_Shotgun.A_Weapons_Unique.Shotgun_Starter_Torgue_Anna',
                    'GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_Torguemada',
                    'GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Old_Hyperion_3_Bullpup'
                    
                ],
                pool_names=[]
            )

        # SMG
        case "Common SMG":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SMG_01_Common")
        case "Uncommon SMG":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SMG_02_Uncommon")
        case "Rare SMG":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SMG_04_Rare")
        case "VeryRare SMG":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SMG_05_VeryRare")
        case "Glitch SMG":
            return create_modified_item_pool(base_pool="GD_Ma_ItemPools.WeaponPools.Pool_Weapons_SMG_Glitch_Marigold")
        case "Legendary SMG":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SMG_06_Legendary")
        case "Unique SMG":
            return create_modified_item_pool("BLGUniqueSMGs",
                inv_bal_def_names=[
                    'GD_Cork_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch',
                    'GD_Cork_Weap_SMG.A_Weapons_Unique.SMG_Bandit_3_MareksMouth',
                    'GD_Cork_Weap_SMG.A_Weapons_Unique.SMG_Bandit_3_MeatGrinder',
                    'GD_Weap_SMG.A_Weapons_Unique.SMG_Dahl_3_Fridgia',
                    'GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_Frostfire',
                    'GD_Cork_Weap_SMG.A_Weapons_Unique.SMG_Old_Hyperion_BlackSnake',
                    # 'GD_Cork_Weap_SMG.A_Weapons_Unique.SMG_Starter_Hyperion_JackD',
                    # 'GD_Cork_Weap_SMG.A_Weapons_Unique.SMG_Starter_Tediore_Fragtrap',
                    'GD_Cork_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_GoodTouch',
                    'GD_Cypressure_Weapons.A_Weapons_Unique.SMG_Bandit_3_FastTalker',
                    'GD_Ma_Weapons.A_Weapons_Unique.SMG_Bandit_6_Glitch_CutieKiller',
                    'GD_Petunia_Weapons.SMGs.SMG_Tediore_3_Boxxy'
                ],
                pool_names=[]
            )

        # SniperRifle
        case "Common SniperRifle":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_01_Common")
        case "Uncommon SniperRifle":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_02_Uncommon")
        case "Rare SniperRifle":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_04_Rare")
        case "VeryRare SniperRifle":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_05_VeryRare", skip_alien=True)
        case "Glitch SniperRifle":
            return create_modified_item_pool(base_pool="GD_Ma_ItemPools.WeaponPools.Pool_Weapons_Sniper_Glitch_Marigold")
        case "Legendary SniperRifle":
            return create_modified_item_pool(
                "BLGLegendarySnipers", 
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_06_Legendary",
                inv_bal_def_names=[
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Dahl_5_Pitchfork",
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Vladof_5_Lyudmila",
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Maliwan_5_Volcano",
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Jakobs_5_Skullmasher",
                    # "GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Hyperion_5_Invader",
                    # "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Longbow",
                    # "GD_Anemone_Weapons.A_Weapons_Unique.Sniper_Jakobs_3_Morde_Lt",
                ]
            )
        case "Unique SniperRifle":
            return create_modified_item_pool("BLGUniqueSnipers",
                inv_bal_def_names=[
                    'GD_Cork_Weap_SniperRifles.A_Weapons_Unique.Sniper_Dahl_3_WetWeek',
                    'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_FremingtonsEdge',
                    'GD_Cork_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Razorback',
                    'GD_Cork_Weap_SniperRifles.A_Weapons_Unique.Sniper_Maliwan_3_ChereAmie',
                    'GD_Cork_Weap_SniperRifles.A_Weapons_Unique.Sniper_Vladof_3_TheMachine',
                    # 'GD_Cork_Weap_SniperRifles.A_Weapons_Unique.Sniper_Starter_Jakobs_Nisha',
                    'GD_Petunia_Weapons.Snipers.Sniper_Jakobs_3_Plunkett',
                ],
                pool_names=[]
            )

        # AssaultRifle
        case "Common AssaultRifle":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_01_Common")
        case "Uncommon AssaultRifle":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_02_Uncommon")
        case "Rare AssaultRifle":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_04_Rare")
        case "VeryRare AssaultRifle":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare")
        case "Glitch AssaultRifle":
            return create_modified_item_pool(base_pool="GD_Ma_ItemPools.WeaponPools.Pool_Weapons_AssaultRifles_Glitch_Marigold")
        case "Legendary AssaultRifle":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_06_Legendary")
        case "Unique AssaultRifle":
            return create_modified_item_pool(
                inv_bal_def_names=[
                    'GD_Cypressure_Weapons.A_Weapons_Unique.AR_Bandit_3_BossNova',
                    'GD_Petunia_Weapons.AssaultRifles.AR_Bandit_3_CryBaby',
                    'gd_cork_weap_assaultrifle.A_Weapons_Unique.AR_Vladof_3_IceScream',
                    'gd_cork_weap_assaultrifle.A_Weapons_Unique.AR_Jakobs_3_Wallop',
                    'gd_cork_weap_assaultrifle.A_Weapons_Unique.AR_Vladof_3_Hail',
                    'gd_cork_weap_assaultrifle.A_Weapons_Unique.AR_Vladof_3_OldPainful',
                ],
                pool_names=[]
            )
        # Laser
        case "Common Laser":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Lasers_01_Common")
        case "Uncommon Laser":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Lasers_02_Uncommon")
        case "Rare Laser":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Lasers_04_Rare")
        case "VeryRare Laser":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Lasers_05_VeryRare")
        case "Glitch Laser":
            return create_modified_item_pool(base_pool="GD_Ma_ItemPools.WeaponPools.Pool_Weapons_Lasers_Glitch_Marigold")
        case "Legendary Laser":
            return create_modified_item_pool(
                "BLGLegendaryARs",
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Lasers_06_Legendary",
                inv_bal_def_names=[
                    # "GD_Aster_Weapons.Lasers.AR_Bandit_3_Ogre",
                    # "GD_Anemone_Weapons.Laser.Brothers.AR_Jakobs_5_Brothers",
                ]
            )
        case "Unique Laser":
            return create_modified_item_pool("BLGUniqueLasers",
                inv_bal_def_names=[
                    'GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Hyperion_3_Mining',
                    'GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Dahl_3_Firestarta',
                    'GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Maliwan_3_Blizzard',
                    'GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Maliwan_3_VibraPulse',
                    'GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Maliwan_4_SavorySideSaber',
                    'GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Tediore_3_Vandergraffen',
                    'GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Maliwan_4_Rosie',
                    'GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Maliwan_4_Egun',
                    'GD_Cork_Weap_Lasers.A_Weapons_Mission.Laser_Maliwan_PerfectHibernation',
                    'GD_Ma_Weapons.A_Weapons_Unique.Laser_Dahl_6_Glitch_HeartfullSplodger',
                    'GD_Ma_Weapons.A_Weapons_Unique.Laser_Maliwan_3_Enlightenment',
                    'GD_Ma_Weapons.A_Weapons_Unique.Laser_Maliwan_3_Minac',
                ],
                pool_names=[]
            )

        # RocketLauncher
        case "Common RocketLauncher":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_01_Common")
        case "Uncommon RocketLauncher":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_02_Uncommon")
        case "Rare RocketLauncher":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_04_Rare")
        case "VeryRare RocketLauncher":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_05_VeryRare")
        case "Glitch RocketLauncher":
            return create_modified_item_pool(base_pool="GD_Ma_ItemPools.WeaponPools.Pool_Weapons_Launchers_Glitch_Marigold")
        case "Legendary RocketLauncher":
            return create_modified_item_pool("BLGLegendaryRPGs",
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_06_Legendary"
            )
        case "Unique RocketLauncher":
            return create_modified_item_pool("BLGUniqueRPGs",
                inv_bal_def_names=[
                    'GD_Cork_Weap_Launchers.A_Weapons_Unique.RL_Tediore_3_Rocketeer',
                    'GD_Cork_Weap_Launchers.A_Weapons_Unique.RL_Torgue_3_Creamer',
                ],
                pool_names=[]
            )

    if gear_kind in individual_receivables_dict:
        return create_modified_item_pool(inv_bal_def_names=[individual_receivables_dict[gear_kind]])

    return (None, [])

def spawn_gear(gear_kind, dist=150, height=0, override_loc=None):
    if type(gear_kind) is int:
        print(f"spawn_gear got int: {gear_kind}")
        return

    (item_pool, cleanup_funcs) = get_item_pool_from_gear_kind(gear_kind)
    if item_pool is None:
        # print("unknown gear kind: " + gear_kind)
        return

    spawn_gear_from_pool(item_pool, dist, height, cleanup_funcs=cleanup_funcs, override_loc=override_loc)

def spawn_gear_from_pool_name(item_pool_name, dist=150, height=0, override_loc=None):
    item_pool = unrealsdk.find_object("ItemPoolDefinition", item_pool_name)
    if not item_pool or item_pool is None:
        print("can't find item pool: " + item_pool_name)
        return
    spawn_gear_from_pool(item_pool, dist, height, override_loc=override_loc)


def spawn_gear_from_pool(item_pool, dist=150, height=0, package_name="BouncyLootGod", cleanup_funcs=[], override_loc=None):
    if not item_pool:
        return

    # spawns item at player
    pc = get_pc()
    if not pc or not pc.Pawn:
        print("skipped spawn")
        return
    package = get_or_create_package(package_name)

    sbsl_obj = unrealsdk.construct_object("Behavior_SpawnLootAroundPoint", package, "blg_spawn")
    # sbsl_obj.ItemPools = [unrealsdk.find_object("ItemPoolDefinition", "GD_Itempools.WeaponPools.Pool_Weapons_Pistols_02_Uncommon")]
    sbsl_obj.SpawnVelocityRelativeTo = 0
    sbsl_obj.bTorque = False
    sbsl_obj.CircularScatterRadius = 0
    # loc = pc.LastKnownLocation
    loc = get_loc_in_front_of_player(dist, height, pc)
    if override_loc:
        loc.X = override_loc["X"]
        loc.Y = override_loc["Y"]
        loc.Z = override_loc["Z"]
    sbsl_obj.CustomLocation = unrealsdk.make_struct("AttachmentLocationData", 
        Location=loc, #unrealsdk.make_struct("Vector", X=loc.X, Y=loc.Y, Z=loc.Z),
        AttachmentBase=None, AttachmentName=""
    )

    # item_pool.MinGameStageRequirement = None
    sbsl_obj.ItemPools = [item_pool]

    sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=0.000000, Y=0.000000, Z=200.000000)
    sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))

    for func in cleanup_funcs:
        func()

    try:
        blg = get_globals()
        if blg:
            blg.loot_spawns_in_progress.add(pc.GetWillowGlobals().PickupList[-1])
    except:
        pass

def activate_moxxitail_skill(skill_name, duration_override=None, name_override=None):
    try:
        skill = unrealsdk.find_object("SkillDefinition", skill_name)
    except:
        unrealsdk.load_package("Spaceport_Combat")
        skill = unrealsdk.find_object("SkillDefinition", skill_name)
        skill.ObjectFlags |= ObjectFlags.KEEP_ALIVE
    activate_skill(skill, duration_override, name_override)
def activate_skill(skill, duration_override=None, name_override=None):
    duration = skill.InitialDuration
    if duration_override:
        skill.InitialDuration = duration_override
    pc = get_pc()
    pc.ServerActivateSkill(skill, None, 5)
    display_claptrapped_ui(title="On the House", duration_override=1.5, skill_name_override=name_override)
    skill.InitialDuration = duration
    
moxxtail_duration = 120 #seconds
def activate_moxxtail(item_id):
    if item_id == item_name_to_id.get("Moxxtail: Moxxis' Choice"):
        drink = random.choice(["Lemon Lime & Bullets", "Gargle Blaster", "Fanalian Toddy", "Squill Syrup", "Penargilon Kangaroo", "Brick's Fist", "Hot Gazpacho", "Replicated Kali-fal"])
        activate_moxxtail(item_name_to_id.get("Moxxtail: " + drink))
    elif item_id == item_name_to_id.get("Moxxtail: Lemon Lime & Bullets"):
        activate_moxxitail_skill("GD_Moxxtails.Skills.Skill_Moxxtail_AmmoRegen", moxxtail_duration, "Moxxtail: Lemon Lime & Bullets")
    elif item_id == item_name_to_id.get("Moxxtail: Gargle Blaster"):
        activate_moxxitail_skill("GD_Moxxtails.Skills.Skill_Moxxtail_DamageBoost", moxxtail_duration, "Moxxtail: Gargle Blaster")
    elif item_id == item_name_to_id.get("Moxxtail: Fanalian Toddy"):
        activate_moxxitail_skill("GD_Moxxtails.Skills.Skill_Moxxtail_DefenseBoost", moxxtail_duration, "Moxxtail: Fanalian Toddy")
    elif item_id == item_name_to_id.get("Moxxtail: Squill Syrup"):
        activate_moxxitail_skill("GD_Moxxtails.Skills.Skill_Moxxtail_Elemental", moxxtail_duration, "Moxxtail: Squill Syrup")
    elif item_id == item_name_to_id.get("Moxxtail: Penargilon Kangaroo"):
        activate_moxxitail_skill("GD_Moxxtails.Skills.Skill_Moxxtail_HealingRegen", moxxtail_duration, "Moxxtail: Penargilon Kangaroo")
    elif item_id == item_name_to_id.get("Moxxtail: Brick's Fist"):
        activate_moxxitail_skill("GD_Moxxtails.Skills.Skill_Moxxtail_MeleeBoost", moxxtail_duration, "Moxxtail: Brick's Fist")
    elif item_id == item_name_to_id.get("Moxxtail: Hot Gazpacho"):
        activate_moxxitail_skill("GD_Moxxtails.Skills.Skill_Moxxtail_SpeedBoost", moxxtail_duration, "Moxxtail: Hot Gazpacho")
    elif item_id == item_name_to_id.get("Moxxtail: Replicated Kali-fal"):
        activate_moxxitail_skill("GD_Moxxtails.Skills.Skill_Moxxtail_OxygenConsumption", moxxtail_duration, "Moxxtail: Replicated Kali-fal")