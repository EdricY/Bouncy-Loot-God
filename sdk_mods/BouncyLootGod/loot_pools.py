import unrealsdk
import unrealsdk.unreal as unreal
from unrealsdk.hooks import Type, Block

import datetime

from mods_base import get_pc, ObjectFlags
from BouncyLootGod.oob import get_loc_in_front_of_player

# some things here adapted from RoguelandsGamemode/Looties.py

# orange = unrealsdk.make_struct("Color", R=128, G=64, B=0, A=255)

def pathname(obj):
    if obj is None:
        return None
    return obj.PathName(obj)

def get_or_create_package(package_name="BouncyLootGod"):
    try:
        return unrealsdk.find_object("Package", package_name)
    except ValueError:
        return unrealsdk.construct_object("Package", None, "BouncyLootGod", ObjectFlags.KEEP_ALIVE)

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

    if inv_bal_def.Class.Name == "WeaponBalanceDefinition":
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
    name="itempool",
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
    "GD_Orchid_Shields.A_Item_Custom.S_BladeShield",
    "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_1340",
    "GD_Sage_Shields.A_Item_Custom.S_BucklerShield",
    "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_PotOGold",
    "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_Order",
    "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_Equitas",
    "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_DeadlyBloom",
    "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_04_LoveThumper",
]

unique_grenade_def_names = [
    "GD_Aster_GrenadeMods.A_Item.GM_Fireball",
    "GD_Aster_GrenadeMods.A_Item.GM_LightningBolt",
    "GD_Aster_GrenadeMods.A_Item.GM_MagicMissileRare",
    "GD_Aster_GrenadeMods.A_Item.GM_MagicMissile",
    "GD_Orchid_GrenadeMods.A_Item_Custom.GM_Blade",
    "GD_GrenadeMods.A_Item_Custom.GM_FusterCluck",
    "GD_GrenadeMods.A_Item_Custom.GM_KissOfDeath",
    "GD_GrenadeMods.A_Item_Custom.GM_SkyRocket",
    "GD_GrenadeMods.A_Item_Legendary.GM_FlameSpurt",
]

unique_relic_def_names = [
    "GD_Artifacts.A_Item_Unique.A_Afterburner",
    "GD_Artifacts.A_Item_Unique.A_Deputy",
    "GD_Artifacts.A_Item_Unique.A_Endowment",
    "GD_Artifacts.A_Item_Unique.A_Opportunity",
    "GD_Artifacts.A_Item_Unique.A_Sheriff",
    "GD_Artifacts.A_Item_Unique.A_VaultHunter",
    "GD_Aster_Artifacts.A_Item_Unique.A_MysteryAmulet",
    "GD_Orchid_Artifacts.A_Item_Unique.A_Blade",
    "GD_Artifacts.A_Item_Unique.A_Terramorphous", # this should go here instead of in it's own category
    "GD_Anemone_Relics.A_Item.A_Elemental_Status_Rare", # winter is over
]

individual_receivables_dict = {
    "12 Pounder":'GD_Orchid_BossWeapons.Launcher.RL_Torgue_3_12Pounder',
    "Actualizer":'GD_Orchid_RaidWeapons.SMG.Actualizer.Orchid_Seraph_Actualizer_Balance',
    "Ahab":'GD_Orchid_RaidWeapons.RPG.Ahab.Orchid_Seraph_Ahab_Balance',
    "Ahab (ERROR)":'GD_Orchid_BossWeapons.RPG.Ahab.Orchid_Boss_Ahab_Balance_NODROP',
    "Amigo Sincero": 'GD_Anemone_Weapons.A_Weapons_Unique.Sniper_Jakobs_3_Morde_Lt',
    "Avenger":'GD_Gladiolus_Weapons.SMG.SMG_Tediore_6_Avenger',
    "Baby Maker":'GD_Weap_SMG.A_Weapons_Legendary.SMG_Tediore_5_BabyMaker',
    "Bad Touch":'GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch',
    "Badaboom":'GD_Weap_Launchers.A_Weapons_Legendary.RL_Bandit_5_BadaBoom',
    "Bane":'GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Bane',
    "Bearcat":'GD_Gladiolus_Weapons.AssaultRifle.AR_Dahl_6_Bearcat',
    "Bekah":'GD_Lobelia_Weapons.AssaultRifles.AR_Jakobs_6_Bekah',
    "Bitch":'GD_Weap_SMG.A_Weapons_Legendary.SMG_Hyperion_5_Bitch',
    "Blockhead":'GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Blockhead',
    "Bone Shredder":'GD_Weap_SMG.A_Weapons_Unique.SMG_Bandit_3_BoneShredder',
    "Boom Puppy":'GD_Iris_Weapons.AssaultRifles.AR_Torgue_3_BoomPuppy',
    "Buffalo":'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Buffalo',
    "Bunny":'GD_Weap_Launchers.A_Weapons_Legendary.RL_Tediore_5_Bunny',
    "Butcher":'GD_Gladiolus_Weapons.Shotgun.SG_Hyperion_6_Butcher',
    "CHOPPER":'GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Jakobs_3_Stomper',
    "Carnage":'GD_Lobelia_Weapons.Shotguns.SG_Torgue_6_Carnage',
    "Chulainn":'GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_Chulainn',
    "Chère-amie":'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Maliwan_3_ChereAmie',
    "Cobra":'GD_Iris_Weapons.SniperRifles.Sniper_Jakobs_3_Cobra',
    "Commerce":'GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Commerce',
    "Conference Call":'GD_Weap_Shotgun.A_Weapons_Legendary.SG_Hyperion_5_ConferenceCall',
    "Creamer":'GD_Weap_Launchers.A_Weapons_Unique.RL_Torgue_3_Creamer',
    "Crit":'GD_Aster_Weapons.SMGs.SMG_Maliwan_3_Crit',
    "Dahlminator":'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Dahlminator',
    "Damned Cowboy":'GD_Sage_Weapons.AssaultRifle.AR_Jakobs_3_DamnedCowboy',
    "Deliverance":'GD_Weap_Shotgun.A_Weapons_Legendary.SG_Tediore_5_Deliverance',
    "Devastator":'GD_Orchid_RaidWeapons.Pistol.Devastator.Orchid_Seraph_Devastator_Balance',
    "Dog":'GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Dog',
    "Elephant Gun":'GD_Sage_Weapons.SniperRifles.Sniper_Jakobs_3_ElephantGun',
    "Emperor":'GD_Weap_SMG.A_Weapons_Legendary.SMG_Dahl_5_Emperor',
    "Evil Smasher":'GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Torgue_3_EvilSmasher',
    "Fibber":'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Fibber',
    "Flakker":'GD_Weap_Shotgun.A_Weapons_Legendary.SG_Torgue_5_Flakker',
    "Florentine":'GD_Aster_RaidWeapons.SMGs.Aster_Seraph_Florentine_Balance',
    "Fremington's Edge":'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_FremingtonsEdge',
    "Godfinger":'GD_Lobelia_Weapons.sniper.Sniper_Jakobs_6_Godfinger',
    "Good Touch":'GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_GoodTouch',
    "Greed":'GD_Orchid_BossWeapons.Pistol.Pistol_Jakobs_ScarletsGreed',
    "Grog Nozzle":'GD_Aster_Weapons.Pistols.Pistol_Maliwan_3_GrogNozzle',
    "Gub":'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Bandit_5_Gub',
    "Gunerang":'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Tediore_5_Gunerang',
    "Gwen's Head":'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_GwensHead',
    "Hail":'GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Vladof_3_Hail',
    "Hammer Buster":'GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Jakobs_5_HammerBuster',
    "Hawk Eye":'GD_Sage_RaidWeapons.sniper.Sage_Seraph_HawkEye_Balance',
    "Heart Breaker":'GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_HeartBreaker',
    "Hector's Paradise":'GD_Anemone_Weapons.A_Weapons_Legendary.Pistol_Dahl_5_Hector_Hornet',
    "Hellfire":'GD_Weap_SMG.A_Weapons_Legendary.SMG_Maliwan_5_HellFire',
    "Hive":'GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_3_TheHive',
    "Hornet":'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Dahl_5_Hornet',
    "Hot Mama":'GD_Anemone_Weapons.sniper.Sniper_Jakobs_6_Chaude_Mama',
    "Hydra":'GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Hydra',
    "Infection":'GD_Sage_RaidWeapons.Pistol.Sage_Seraph_Infection_Balance',
    "Infection Cleaner":'GD_Anemone_Weapons.SMG.SMG_Tediore_6_Infection_Cleaner',
    "Infinity":'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Vladof_5_Infinity',
    "Interfacer":'GD_Sage_RaidWeapons.Shotgun.Sage_Seraph_Interfacer_Balance',
    "Invader":'GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Hyperion_5_Invader',
    "Jolly Roger":'GD_Orchid_BossWeapons.Shotgun.SG_Bandit_3_JollyRoger',
    "Judge":'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Judge',
    "KerBlaster":'GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Torgue_5_KerBlaster',
    "Kitten":'GD_Iris_Weapons.AssaultRifles.AR_Vladof_3_Kitten',
    "Lady Fist":'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_LadyFist',
    "Landscaper":'GD_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_Landscaper',
    "Lascaux":'GD_Weap_SMG.A_Weapons_Unique.SMG_Dahl_3_Lascaux',
    "Law":'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Law',
    "Lead Storm":'GD_Sage_RaidWeapons.AssaultRifle.Sage_Seraph_LeadStorm_Balance',
    "Little Evie":'GD_Orchid_BossWeapons.Pistol.Pistol_Maliwan_3_LittleEvie',
    "Logan's Gun":'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Hyperion_5_LogansGun',
    "Longbow":'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Longbow',
    "Lyuda":'GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Vladof_5_Lyudmila',
    "M2828 Thumpson": 'GD_Anemone_Weapons.AssaultRifle.Brothers.AR_Jakobs_5_Brothers',
    "Madhous!": 'GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Bandit_5_Madhouse',
    "Maggie":'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Jakobs_5_Maggie',
    "Mongol":'GD_Weap_Launchers.A_Weapons_Legendary.RL_Vladof_5_Mongol',
    "Morningstar":'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Morningstar',
    "Nirvana": 'GD_Anemone_Weapons.A_Weapons_Legendary.SMG_Maliwan_5_HellFire',
    "Norfleet":'GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_Alien_Norfleet',
    "Nukem":'GD_Weap_Launchers.A_Weapons_Legendary.RL_Torgue_5_Nukem',
    "Octo":'GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Octo',
    "Ogre":'GD_Aster_Weapons.AssaultRifles.AR_Bandit_3_Ogre',
    "Omen":'GD_Aster_RaidWeapons.Shotguns.Aster_Seraph_Omen_Balance',
    "Orc":'GD_Aster_Weapons.SMGs.SMG_Bandit_3_Orc',
    "Orphan Maker":'GD_Orchid_BossWeapons.Shotgun.SG_Jakobs_3_OrphanMaker',
    "Overcompensator":'GD_Anemone_Weapons.Shotgun.Overcompensator.SG_Hyperion_6_Overcompensator',
    "Patriot":'GD_Orchid_RaidWeapons.sniper.Patriot.Orchid_Seraph_Patriot_Balance',
    "Peak Opener":'GD_Anemone_Weapons.AssaultRifle.PeakOpener.AR_PeakOpener',
    "Pimpernel":'GD_Orchid_BossWeapons.SniperRifles.Sniper_Maliwan_3_Pimpernel',
    "Pitchfork":'GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Dahl_5_Pitchfork',
    "Pocket Rocket":'GD_Iris_Weapons.Pistols.Pistol_Torgue_3_PocketRocket',
    "Pyrophobia":'GD_Anemone_Weapons.Rocket_Launcher.RL_Maliwan_5_Pyrophobia',
    "Rapier":'GD_Orchid_BossWeapons.AssaultRifle.AR_Vladof_3_Rapier',
    "Retcher": 'GD_Orchid_RaidWeapons.Shotgun.Spitter.Orchid_Seraph_Spitter_Balance',
    "Rex":'GD_Sage_Weapons.Pistols.Pistol_Jakobs_3_Rex',
    "Roaster":'GD_Weap_Launchers.A_Weapons_Unique.RL_Bandit_3_Roaster',
    "RokSalt":'GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_RokSalt',
    "Rubi":'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Maliwan_3_Rubi',
    "SWORDSPLOSION":'GD_Aster_Weapons.Shotguns.SG_Torgue_3_SwordSplosion',
    "Sand Hawk":'GD_Orchid_BossWeapons.SMG.SMG_Dahl_3_SandHawk',
    "Sawbar":'GD_Gladiolus_Weapons.AssaultRifle.AR_Bandit_6_Sawbar',
    "Scorpio":'GD_Weap_Scorpio.A_Weapon.WeapBalance_Scorpio',
    "Seeker":'GD_Aster_RaidWeapons.AssaultRifles.Aster_Seraph_Seeker_Balance',
    "Seraphim":'GD_Orchid_RaidWeapons.AssaultRifle.Seraphim.Orchid_Seraph_Seraphim_Balance',
    "Shotgun 1340":'GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_Shotgun1340',
    "Shredifier":'GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Vladof_5_Sherdifier',
    "Skullmasher":'GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Jakobs_5_Skullmasher',
    "Slagga":'GD_Weap_SMG.A_Weapons_Legendary.SMG_Bandit_5_Slagga',
    "Sledge's Shotgun":'GD_Weap_Shotgun.A_Weapons_Legendary.SG_Bandit_5_SledgesShotgun',
    "Sloth":'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Dahl_3_Sloth',
    "Slow Hand":'GD_Iris_Weapons.Shotguns.SG_Hyperion_3_SlowHand',
    "Stalker":'GD_Gladiolus_Weapons.Pistol.Pistol_Vladof_6_Stalker',
    "Stinger":'GD_Aster_RaidWeapons.Pistols.Aster_Seraph_Stinger_Balance',
    "Stinkpot":'GD_Orchid_BossWeapons.AssaultRifle.AR_Jakobs_3_Stinkpot',
    "Stomper":'GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Jakobs_3_Stomper',
    "Storm":'GD_Gladiolus_Weapons.sniper.Sniper_Maliwan_6_Storm',
    "Striker":'GD_Weap_Shotgun.A_Weapons_Legendary.SG_Jakobs_5_Striker',
    "Tattler":'GD_Orchid_RaidWeapons.SMG.Tattler.Orchid_Seraph_Tattler_Balance',
    "Teapot":'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Teapot',
    "Teeth of Terramorphous":'GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Teeth',
    "Thunderball Fists":'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Maliwan_5_ThunderballFists',
    "Tidal Wave":'GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_TidalWave',
    "Tinderbox":'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Bandit_3_Tenderbox',
    "Toothpick":'GD_Anemone_Weapons.AssaultRifle.AR_Dahl_6_Toothpick',
    "Trespasser":'GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Tresspasser',
    "Triquetra":'GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_Triquetra',
    "Tunguska":'GD_Gladiolus_Weapons.Launchers.RL_Torgue_6_Tunguska',
    "Twister":'GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Twister',
    "Unforgiven":'GD_Gladiolus_Weapons.Pistol.Pistol_Jakobs_6_Unforgiven',
    "Unicornsplosion":'GD_Anemone_Weapons.Shotguns.SG_Torgue_3_SwordSplosion_Unico',
    "Unkempt Harold":'GD_Weap_Pistol.A_Weapons_Legendary.Pistol_Torgue_5_Calla',
    "Veritas":'GD_Weap_Pistol.A_Weapons_Unique.Pistol_Vladof_3_Veritas',
    "Veruc":'GD_Weap_AssaultRifle.A_Weapons_Legendary.AR_Dahl_5_Veruc',
    "Volcano":'GD_Weap_SniperRifles.A_Weapons_Legendary.Sniper_Maliwan_5_Volcano',
    "Wanderlust":'GD_Lobelia_Weapons.Pistol.Pistol_Maliwan_6_Wanderlust',
    "World Burn":'GD_Anemone_Weapons.Rocket_Launcher.WorldBurn.RL_Torgue_5_WorldBurn',
    "Yellow Jacket":'GD_Sage_Weapons.SMG.SMG_Hyperion_3_YellowJacket',
    "1340 Shield":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_1340',
    "Aequitas":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_Equitas',
    "Antagonist":'GD_Aster_ItemGrades.Shields.Aster_Seraph_Antagonist_Shield_Balance',
    "Big Boom Blaster":'GD_Iris_SeraphItems.BigBoomBlaster.Iris_Seraph_Shield_Booster_Balance',
    "Black Hole":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Singularity',
    "Blockade":'GD_Aster_ItemGrades.Shields.Aster_Seraph_Blockade_Shield_Balance',
    "Cracked Sash":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_CrackedSash',
    "Deadly Bloom":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_DeadlyBloom',
    "Easy Mode":'GD_Anemone_ItemPools.Shields.ItemGrade_Gear_Shield_Nova_Singularity_Peak',
    "Evolution":'GD_Orchid_RaidWeapons.Shield.Anshin.Orchid_Seraph_Anshin_Shield_Balance',
    "Fabled Tortoise":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_05_Legendary',
    "Flame of the Firehawk":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Phoenix',
    "Hide of Terramorphous":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_ThresherRaid',
    "Hoplite":'GD_Iris_SeraphItems.Hoplite.Iris_Seraph_Shield_Juggernaut_Balance',
    "Impaler":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_05_Legendary',
    "Love Thumper":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_04_LoveThumper',
    "Manly Man Shield":'GD_Orchid_Shields.A_Item_Custom.S_BladeShield',
    "Neogenator":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_05_Legendary',
    "Order":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_Order',
    "Pot O' Gold":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_PotOGold',
    "Pun-chee":'GD_Iris_SeraphItems.Pun-chee.Iris_Seraph_Shield_Pun-chee_Balance',
    "Retainer":'GD_Anemone_Balance_Treasure.Shields.ItemGrade_Gear_Shield_Worming',
    "Sponge":'GD_Iris_SeraphItems.Sponge.Iris_Seraph_Shield_Sponge_Balance',
    "The Bee":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_05_Legendary',
    "The Cradle":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_05_Legendary',
    "The Rough Rider":'GD_Sage_Shields.A_Item_Custom.S_BucklerShield',
    "The Sham":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryNormal',
    "The Transformer":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryShock',
    "Whisky Tango Foxtrot":'GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_05_Legendary',
    "Antifection":'GD_Anemone_GrenadeMods.A_Item_Legendary.GM_Antifection',
    "Bonus Package":'GD_GrenadeMods.A_Item_Legendary.GM_BonusPackage',
    "Bouncing Bonny":'GD_GrenadeMods.A_Item_Legendary.GM_BouncingBonny',
    "Breath of Terramorphous":'GD_GrenadeMods.A_Item_Legendary.GM_FlameSpurt',
    "Chain Lightning":'GD_Aster_GrenadeMods.A_Item.GM_ChainLightning',
    "Contraband Sky Rocket":'GD_GrenadeMods.A_Item_Custom.GM_SkyRocket',
    "Crossfire":'GD_Iris_SeraphItems.Crossfire.Iris_Seraph_GrenadeMod_Crossfire_Balance',
    "Fastball":'GD_GrenadeMods.A_Item_Legendary.GM_Fastball',
    "Fire Bee":'GD_GrenadeMods.A_Item_Legendary.GM_FireBee',
    "Fire Storm":'GD_Aster_GrenadeMods.A_Item.GM_FireStorm',
    "Fireball":'GD_Aster_GrenadeMods.A_Item.GM_Fireball',
    "Fuster Cluck":'GD_GrenadeMods.A_Item_Custom.GM_FusterCluck',
    "Kiss of Death":'GD_GrenadeMods.A_Item_Custom.GM_KissOfDeath',
    "Leech":'GD_GrenadeMods.A_Item_Legendary.GM_Leech',
    "Lightning Bolt":'GD_Aster_GrenadeMods.A_Item.GM_LightningBolt',
    "Magic Missile":'GD_Aster_GrenadeMods.A_Item.GM_MagicMissile',
    "Magic Missile (Purple)":'GD_Aster_GrenadeMods.A_Item.GM_MagicMissileRare',
    "Meteor Shower":'GD_Iris_SeraphItems.MeteorShower.Iris_Seraph_GrenadeMod_MeteorShower_Balance',
    "Midnight Star":'GD_Orchid_GrenadeMods.A_Item_Custom.GM_Blade',
    "Nasty Surprise":'GD_GrenadeMods.A_Item_Legendary.GM_NastySurprise',
    "O-Negative":'GD_Iris_SeraphItems.ONegative.Iris_Seraph_GrenadeMod_ONegative_Balance',
    "Pandemic":'GD_GrenadeMods.A_Item_Legendary.GM_Pandemic',
    "Quasar":'GD_GrenadeMods.A_Item_Legendary.GM_Quasar',
    "Rolling Thunder":'GD_GrenadeMods.A_Item_Legendary.GM_RollingThunder',
    "Storm Front":'GD_GrenadeMods.A_Item_Legendary.GM_StormFront',
    "The Electric Chair":'GD_Anemone_GrenadeMods.A_Item_Legendary.GM_StormFront',
    "Blood of Terramorphous":'GD_Artifacts.A_Item_Unique.A_Terramorphous',
    "Blood of the Ancients":'GD_Gladiolus_Artifacts.A_Item.A_VitalityStockpile_VeryRare',
    "Blood of the Seraphs":'GD_Orchid_Artifacts.A_Item_Unique.A_SeraphBloodRelic',
    "Bone of the Ancients":'GD_Gladiolus_Artifacts.A_Item.A_ElementalProficiency_VeryRare',
    "Breath of the Seraphs":'GD_Sage_Artifacts.A_Item.A_SeraphBreath',
    "Deputy's Badge":'GD_Artifacts.A_Item_Unique.A_Deputy',
    "Hard Carry":'GD_Anemone_Relics.A_Item_Unique.A_Deputy',
    "Heart of the Ancients":'GD_Aster_Artifacts.A_Item_Unique.A_SeraphShadow',
    "Lucrative Opportunity":'GD_Artifacts.A_Item_Unique.A_Opportunity',
    "Might of the Seraphs":'GD_Iris_SeraphItems.Might.Iris_Seraph_Artifact_Might_Balance',
    "Mouthwash":'GD_Anemone_Relics.A_Item_Unique.A_Sheriff',
    "Moxxi's Endowment":'GD_Artifacts.A_Item_Unique.A_Endowment',
    "Mysterious Amulet":'GD_Aster_Artifacts.A_Item_Unique.A_MysteryAmulet',
    "Otto Idol":'GD_Orchid_Artifacts.A_Item_Unique.A_Blade',
    "Shadow of the Seraphs":'GD_Aster_Artifacts.A_Item_Unique.A_SeraphShadow',
    "Sheriff's Badge":'GD_Artifacts.A_Item_Unique.A_Sheriff',
    "Skin of the Ancients":'GD_Gladiolus_Artifacts.A_Item.A_ResistanceProtection_VeryRare',
    "The Afterburner":'GD_Artifacts.A_Item_Unique.A_Afterburner',
    "Vault Hunter's Relic":'GD_Artifacts.A_Item_Unique.A_VaultHunter',
    "Winter is Over":'GD_Anemone_Relics.A_Item.A_Elemental_Status_Rare',
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
            return create_modified_item_pool("BLGLegendaryShields", inv_bal_def_names=[
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Singularity",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryShock",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryNormal",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_05_Legendary",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_ThresherRaid",
                "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Phoenix",
            ])
        case "Seraph Shield":
            return create_modified_item_pool("BLGSeraphShields",
                inv_bal_def_names=[
                    "GD_Aster_ItemGrades.Shields.Aster_Seraph_Blockade_Shield_Balance",
                    "GD_Aster_ItemGrades.Shields.Aster_Seraph_Antagonist_Shield_Balance",
                    "GD_Iris_SeraphItems.BigBoomBlaster.Iris_Seraph_Shield_Booster_Balance",
                    "GD_Iris_SeraphItems.Hoplite.Iris_Seraph_Shield_Juggernaut_Balance",
                    "GD_Iris_SeraphItems.Pun-chee.Iris_Seraph_Shield_Pun-chee_Balance",
                    "GD_Iris_SeraphItems.Sponge.Iris_Seraph_Shield_Sponge_Balance",
                    "GD_Orchid_RaidWeapons.Shield.Anshin.Orchid_Seraph_Anshin_Shield_Balance",
                ]
            )
        case "Rainbow Shield":
            return create_modified_item_pool("BLGRainbowShields",
                inv_bal_def_names=[
                    "GD_Anemone_ItemPools.Shields.ItemGrade_Gear_Shield_Nova_Singularity_Peak", # has high spawn modifier
                    # "GD_Anemone_Balance_Treasure.Shields.ItemGrade_Gear_Shield_Worming",
                ],
                pool_names=[
                    "GD_Anemone_ItemPools.ShieldPools.Pool_Shields_Standard_06_Legendary",
                ]
            )
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
                    "GD_Aster_GrenadeMods.A_Item.GM_FireStorm",
                    "GD_Aster_GrenadeMods.A_Item.GM_ChainLightning",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_BonusPackage",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_BouncingBonny",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_Fastball",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_FireBee",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_Leech",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_Pandemic",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_Quasar",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_RollingThunder",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_StormFront",
                    # "GD_GrenadeMods.A_Item_Legendary.GM_NastySurprise",
                ]
            )
        case "Seraph GrenadeMod":
            return create_modified_item_pool(
                inv_bal_def_names=[
                    "GD_Iris_SeraphItems.Crossfire.Iris_Seraph_GrenadeMod_Crossfire_Balance",
                    "GD_Iris_SeraphItems.MeteorShower.Iris_Seraph_GrenadeMod_MeteorShower_Balance",
                    "GD_Iris_SeraphItems.ONegative.Iris_Seraph_GrenadeMod_ONegative_Balance",
                ]
            )
        case "Rainbow GrenadeMod":
            return create_modified_item_pool(
                inv_bal_def_names=[
                    "GD_Anemone_GrenadeMods.A_Item_Legendary.GM_Antifection",
                    "GD_Anemone_GrenadeMods.A_Item_Legendary.GM_StormFront",
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
                    "GD_Itempools.ClassModPools.Pool_ClassMod_06_Legendary",
                    "GD_Itempools.ClassModPools.Pool_ClassMod_06_SlayerOfTerramorphous",
                    # lobelia has 3 elements per character, so add it 3 times to balance
                    "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All", 
                    "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All",
                    "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All",
                ],
                uniform_probability=False,
            )

        # Relic
        case "Common Relic":
            return create_modified_item_pool("BLGCommonRelic",
                base_pool="GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
                relic_rarity="Common",
            )
        case "Uncommon Relic":
            return create_modified_item_pool("BLGUncommonRelic",
                base_pool="GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
                relic_rarity="Uncommon",
            )
        case "Rare Relic":
            return create_modified_item_pool("BLGRareRelic",
                base_pool="GD_Itempools.ArtifactPools.Pool_Artifacts_03_Rare",
                relic_rarity="Rare",
            )
        case "VeryRare Relic":
            return create_modified_item_pool("BLGVeryRareRelic",
                base_pool="GD_Itempools.ArtifactPools.Pool_Artifacts_03_Rare",
                relic_rarity="VeryRare",
            )
        case "E-Tech Relic":
            return create_modified_item_pool("BLGETechRelic",
                pool_names=[
                    "GD_Gladiolus_Itempools.ArtifactPools.Pool_Artifacts_Ancient_AggressionTenacity"
                ],
                inv_bal_def_names=[
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityAssault_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityLauncher_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityPistol_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacityShotgun_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacitySMG_VeryRare",
                    # "GD_Gladiolus_Artifacts.A_Item.A_AggressionTenacitySniper_VeryRare",
                    "GD_Gladiolus_Artifacts.A_Item.A_ElementalProficiency_VeryRare",
                    "GD_Gladiolus_Artifacts.A_Item.A_ResistanceProtection_VeryRare",
                    "GD_Gladiolus_Artifacts.A_Item.A_VitalityStockpile_VeryRare",
                ],
            )
        # case "Legendary Relic":
            # "GD_Artifacts.A_Item_Unique.A_Terramorphous", # we should just call this unique
        case "Seraph Relic":
            return create_modified_item_pool("BLGSeraphRelic", inv_bal_def_names=[
                "GD_Orchid_Artifacts.A_Item_Unique.A_SeraphBloodRelic",
                "GD_Sage_Artifacts.A_Item.A_SeraphBreath",
                "GD_Iris_SeraphItems.Might.Iris_Seraph_Artifact_Might_Balance",
                "GD_Aster_Artifacts.A_Item_Unique.A_SeraphShadow",
            ])
        case "Rainbow Relic":
            return create_modified_item_pool("BLGRainbowRelic", inv_bal_def_names=[
                "GD_Anemone_Relics.A_Item_Unique.A_Deputy",
                "GD_Anemone_Relics.A_Item_Unique.A_Sheriff",
            ])
        # case "Pearlescent Relic":
        case "Unique Relic":
            return create_modified_item_pool("BLGUniqueRelic",
                inv_bal_def_names=unique_relic_def_names
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
        case "E-Tech Pistol":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_05_VeryRare_Alien")
        case "Legendary Pistol":
            return create_modified_item_pool("BLGLegendaryPistols",
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_06_Legendary",
                pool_names=[
                    "GD_Anemone_ItemPools.WeaponPools.Pool_Pistol_Hector_Paradise",
                    # "GD_Anemone_Weapons.A_Weapons_Legendary.Pistol_Vladof_5_Infinity_DD" # Fire Drill
                    # "GD_Anemone_Weapons.Testing_Resist_100.100_Fire",
                ]
            )
        case "Seraph Pistol":
            return create_modified_item_pool("BLGSeraphPistols", inv_bal_def_names=[
                "GD_Aster_RaidWeapons.Pistols.Aster_Seraph_Stinger_Balance",
                "GD_Sage_RaidWeapons.Pistol.Sage_Seraph_Infection_Balance",
                "GD_Orchid_RaidWeapons.Pistol.Devastator.Orchid_Seraph_Devastator_Balance",
            ])


        # case "Rainbow Pistol": # n/a
        case "Pearlescent Pistol":
            return create_modified_item_pool("BLGPearlPistol", inv_bal_def_names=[
                "GD_Lobelia_Weapons.Pistol.Pistol_Maliwan_6_Wanderlust",
                "GD_Gladiolus_Weapons.Pistol.Pistol_Jakobs_6_Unforgiven",
                "GD_Gladiolus_Weapons.Pistol.Pistol_Vladof_6_Stalker",
            ])
        case "Unique Pistol":
            return create_modified_item_pool("BLGUniquePistols",
                inv_bal_def_names=[
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Fibber",
                    "GD_Orchid_BossWeapons.Pistol.Pistol_Jakobs_ScarletsGreed",
                    "GD_Aster_Weapons.Pistols.Pistol_Maliwan_3_GrogNozzle",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_GwensHead",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Judge",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_LadyFist",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Law",
                    "GD_Orchid_BossWeapons.Pistol.Pistol_Maliwan_3_LittleEvie",
                    "GD_Iris_Weapons.Pistols.Pistol_Torgue_3_PocketRocket",
                    "GD_Sage_Weapons.Pistols.Pistol_Jakobs_3_Rex",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Maliwan_3_Rubi",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Teapot",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Bandit_3_Tenderbox",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Vladof_3_Veritas",
                    # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_Starter",
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Dahlminator",
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
        case "E-Tech Shotgun":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_05_VeryRare_Alien")
        case "Legendary Shotgun":
            return create_modified_item_pool("BLGLegendaryShotguns", 
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Shotguns_06_Legendary",
                inv_bal_def_names=[
                    "GD_Anemone_Weapons.Shotgun.Overcompensator.SG_Hyperion_6_Overcompensator"
                ]
            )
        case "Seraph Shotgun":
            return create_modified_item_pool("BLGSeraphShotgun", inv_bal_def_names=[
                "GD_Orchid_RaidWeapons.Shotgun.Spitter.Orchid_Seraph_Spitter_Balance",
                "GD_Aster_RaidWeapons.Shotguns.Aster_Seraph_Omen_Balance",
                "GD_Sage_RaidWeapons.Shotgun.Sage_Seraph_Interfacer_Balance",
            ])
        case "Rainbow Shotgun":
            return create_modified_item_pool("BLGRainbowShotgun", inv_bal_def_names=[
                "GD_Anemone_Weapons.Shotguns.SG_Torgue_3_SwordSplosion_Unico",
            ])
        case "Pearlescent Shotgun":
            return create_modified_item_pool("BLGPearlShotgun", inv_bal_def_names=[
                "GD_Gladiolus_Weapons.Shotgun.SG_Hyperion_6_Butcher",
                "GD_Lobelia_Weapons.Shotguns.SG_Torgue_6_Carnage",
            ])

        case "Unique Shotgun":
            return create_modified_item_pool("BLGUniqueShotguns",
                inv_bal_def_names=[
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Blockhead",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Dog",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_HeartBreaker",
                    "GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Hydra",
                    "GD_Orchid_BossWeapons.Shotgun.SG_Bandit_3_JollyRoger",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_Landscaper",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Tediore_3_Octo",
                    "GD_Orchid_BossWeapons.Shotgun.SG_Jakobs_3_OrphanMaker",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_RokSalt",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_Shotgun1340",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Bandit_3_Teeth",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_TidalWave",
                    "GD_Weap_Shotgun.A_Weapons_Unique.SG_Jakobs_3_Triquetra",
                    "GD_Sage_Weapons.Shotgun.SG_Jakobs_3_Twister",
                    "GD_Aster_Weapons.Shotguns.SG_Torgue_3_SwordSplosion",
                    "GD_Iris_Weapons.Shotguns.SG_Hyperion_3_SlowHand",
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
        case "E-Tech SMG":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SMG_05_VeryRare_Alien")
        case "Legendary SMG":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SMG_06_Legendary")
        case "Seraph SMG":
            return create_modified_item_pool("BLGSeraphSMG", inv_bal_def_names=[
                "GD_Orchid_RaidWeapons.SMG.Tattler.Orchid_Seraph_Tattler_Balance",
                "GD_Aster_RaidWeapons.SMGs.Aster_Seraph_Florentine_Balance",
                "GD_Orchid_RaidWeapons.SMG.Actualizer.Orchid_Seraph_Actualizer_Balance",
            ])

        case "Rainbow SMG":
            return create_modified_item_pool("BLGRainbowSMG", inv_bal_def_names=[
                "GD_Anemone_Weapons.SMG.SMG_Tediore_6_Infection_Cleaner",
                "GD_Anemone_Weapons.A_Weapons_Legendary.SMG_Maliwan_5_HellFire",
            ])

        case "Pearlescent SMG":
            return create_modified_item_pool("BLGPearlSMG", inv_bal_def_names=[
                "GD_Gladiolus_Weapons.SMG.SMG_Tediore_6_Avenger",
            ])
        case "Unique SMG":
            return create_modified_item_pool("BLGUniqueSMGs",
                inv_bal_def_names=[
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Bandit_3_BoneShredder",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Dahl_3_Lascaux",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Gearbox_1",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Bane",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Commerce",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_Chulainn",
                    "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_GoodTouch",
                    "GD_Sage_Weapons.SMG.SMG_Hyperion_3_YellowJacket",
                    "GD_Orchid_BossWeapons.SMG.SMG_Dahl_3_SandHawk",
                    "GD_Aster_Weapons.SMGs.SMG_Bandit_3_Orc",
                    "GD_Aster_Weapons.SMGs.SMG_Maliwan_3_Crit",
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
        case "E-Tech SniperRifle":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SniperRifles_05_VeryRare_Alien")
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
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Longbow",
                    "GD_Anemone_Weapons.A_Weapons_Unique.Sniper_Jakobs_3_Morde_Lt",
                ]
            )
        case "Seraph SniperRifle":
            return create_modified_item_pool("BLGSeraphSniper", inv_bal_def_names=[
                "GD_Orchid_RaidWeapons.sniper.Patriot.Orchid_Seraph_Patriot_Balance",
                "GD_Sage_RaidWeapons.sniper.Sage_Seraph_HawkEye_Balance",
            ])
        case "Rainbow SniperRifle":
            return create_modified_item_pool("BLGRainbowSniper", inv_bal_def_names=[
                "GD_Anemone_Weapons.sniper.Sniper_Jakobs_6_Chaude_Mama",
            ])
        case "Pearlescent SniperRifle":
            return create_modified_item_pool("BLGPearlSniper", inv_bal_def_names=[
                "GD_Gladiolus_Weapons.sniper.Sniper_Maliwan_6_Storm",
                "GD_Lobelia_Weapons.sniper.Sniper_Jakobs_6_GodFinger",
            ])
        case "Unique SniperRifle":
            return create_modified_item_pool("BLGUniqueSnipers",
                inv_bal_def_names=[
                    "GD_Sage_Weapons.SniperRifles.Sniper_Jakobs_3_ElephantGun",
                    "GD_Orchid_BossWeapons.SniperRifles.Sniper_Maliwan_3_Pimpernel",
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Buffalo",
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Maliwan_3_ChereAmie",
                    "GD_Iris_Weapons.SniperRifles.Sniper_Jakobs_3_Cobra",
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_FremingtonsEdge",
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Morningstar",
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Dahl_3_Sloth",
                    "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Tresspasser",
                    # "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Gearbox_1",

                    # GD_Aster_Weapons.Snipers.SR_Dahl_4_Emerald
                    # GD_Aster_Weapons.Snipers.SR_Hyperion_4_Diamond
                    # GD_Aster_Weapons.Snipers.SR_Jakobs_4_Citrine
                    # GD_Aster_Weapons.Snipers.SR_Maliwan_4_Aquamarine
                    # GD_Aster_Weapons.Snipers.SR_Vladof_4_Garnet
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
        case "E-Tech AssaultRifle":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_05_VeryRare_Alien")
        case "Legendary AssaultRifle":
            return create_modified_item_pool(
                "BLGLegendaryARs",
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_06_Legendary",
                inv_bal_def_names=[
                    "GD_Aster_Weapons.AssaultRifles.AR_Bandit_3_Ogre",
                    "GD_Anemone_Weapons.AssaultRifle.Brothers.AR_Jakobs_5_Brothers",
                ]
            )
        case "Seraph AssaultRifle":
            return create_modified_item_pool("BLGSeraphAR", inv_bal_def_names=[
                "GD_Orchid_RaidWeapons.AssaultRifle.Seraphim.Orchid_Seraph_Seraphim_Balance",
                "GD_Aster_RaidWeapons.AssaultRifles.Aster_Seraph_Seeker_Balance",
                "GD_Sage_RaidWeapons.AssaultRifle.Sage_Seraph_LeadStorm_Balance",
            ])

        case "Rainbow AssaultRifle":
            return create_modified_item_pool("BLGRainbowAR", inv_bal_def_names=[
                "GD_Anemone_Weapons.AssaultRifle.AR_Dahl_6_Toothpick",
                "GD_Anemone_Weapons.AssaultRifle.PeakOpener.AR_Torgue_5_PeakOpener",
                # "GD_Anemone_Weapons.AssaultRifle.PeakOpener.AR_PeakOpener", # nope
            ])

        case "Pearlescent AssaultRifle":
            return create_modified_item_pool("BLGPearlAR", inv_bal_def_names=[
                "GD_Gladiolus_Weapons.AssaultRifle.AR_Bandit_6_Sawbar",
                "GD_Lobelia_Weapons.AssaultRifles.AR_Jakobs_6_Bekah",
                "GD_Gladiolus_Weapons.AssaultRifle.AR_Dahl_6_Bearcat",
            ])

        case "Unique AssaultRifle":
            return create_modified_item_pool("BLGUniqueARs",
                inv_bal_def_names=[
                    "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_3_Scorpio",
                    "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Jakobs_3_Stomper",
                    "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Torgue_3_EvilSmasher",
                    "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Vladof_3_Hail",
                    "GD_Sage_Weapons.AssaultRifle.AR_Jakobs_3_DamnedCowboy",
                    "GD_Sage_Weapons.AssaultRifle.AR_Bandit_3_Chopper",
                    "GD_Iris_Weapons.AssaultRifles.AR_Torgue_3_BoomPuppy",
                    "GD_Iris_Weapons.AssaultRifles.AR_Vladof_3_Kitten",
                    "GD_Orchid_BossWeapons.AssaultRifle.AR_Jakobs_3_Stinkpot",
                    "GD_Orchid_BossWeapons.AssaultRifle.AR_Vladof_3_Rapier",
                    # GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Dahl_1_GBX
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
        case "E-Tech RocketLauncher":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_05_VeryRare_Alien")
        case "Legendary RocketLauncher":
            return create_modified_item_pool("BLGLegendaryRPGs",
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_06_Legendary",
                inv_bal_def_names=[
                    "GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_Alien_Norfleet"
                ]
            )

        case "Seraph RocketLauncher":
            return create_modified_item_pool("BLGSeraphRPGs", inv_bal_def_names=[
                "GD_Orchid_RaidWeapons.RPG.Ahab.Orchid_Seraph_Ahab_Balance",
                "GD_Orchid_BossWeapons.RPG.Ahab.Orchid_Boss_Ahab_Balance_NODROP",
            ])

        case "Rainbow RocketLauncher":
            return create_modified_item_pool("BLGRainbowRPGs", inv_bal_def_names=[
                "GD_Anemone_Weapons.Rocket_Launcher.WorldBurn.RL_Torgue_5_WorldBurn",
            ])

        case "Pearlescent RocketLauncher":
            return create_modified_item_pool("BLGPearlRPGs", inv_bal_def_names=[
                "GD_Gladiolus_Weapons.Launchers.RL_Torgue_6_Tunguska",
            ])
        case "Unique RocketLauncher":
            return create_modified_item_pool("BLGUniqueRPGs",
                inv_bal_def_names=[
                    "GD_Weap_Launchers.A_Weapons_Unique.RL_Bandit_3_Roaster",
                    "GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_3_TheHive",
                    "GD_Weap_Launchers.A_Weapons_Unique.RL_Torgue_3_Creamer",
                    "GD_Orchid_BossWeapons.Launcher.RL_Torgue_3_12Pounder",
                ],
                pool_names=[]
            )

        case "YellowCandy":
            return (unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_YellowCandy"), [])
        case "RedCandy":
            return (unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_RedCandy"), [])
        case "GreenCandy":
            return (unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_GreenCandy"), [])
        case "BlueCandy":
            return (unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_BlueCandy"), [])
        # case 9000:
        #     return (unrealsdk.find_object("ItemPoolDefinition", "GD_Flax_ItemPools.Items.ItemPool_Flax_Candy"), [])
        # case 9001:
        #     return create_modified_item_pool("BLGMoxxiGuns",
        #         inv_bal_def_names=[
        #             "GD_Weap_Launchers.A_Weapons_Unique.RL_Torgue_3_Creamer",
        #             "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch",
        #             "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_GoodTouch",
        #             "GD_Aster_Weapons.SMGs.SMG_Maliwan_3_Crit",
        #             "GD_Aster_Weapons.Pistols.Pistol_Maliwan_3_GrogNozzle",
        #             "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Maliwan_3_Rubi",
        #             "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Maliwan_3_ChereAmie",
        #             "GD_Weap_Shotgun.A_Weapons_Unique.SG_Hyperion_3_HeartBreaker",
        #             "GD_Iris_Weapons.Shotguns.SG_Hyperion_3_SlowHand",
        #             "GD_Weap_AssaultRifle.A_Weapons_Unique.AR_Vladof_3_Hail",
        #             "GD_Iris_Weapons.AssaultRifles.AR_Vladof_3_Kitten",
        #         ],
        #         pool_names=[]
        #     )
        # case 9002:
        #     return create_modified_item_pool(base_pool="GD_Aster_ItemPools.WeaponPools.Pool_Weapons_04_Gemstone")

        case "Gemstone Pistol":
            return create_modified_item_pool(base_pool="GD_Aster_ItemPools.WeaponPools.Pool_Weapons_Pistols_04_Gemstone")
        case "Gemstone Shotgun":
            return create_modified_item_pool(base_pool="GD_Aster_ItemPools.WeaponPools.Pool_Weapons_Shotguns_04_Gemstone")
        case "Gemstone SMG":
            return create_modified_item_pool(base_pool="GD_Aster_ItemPools.WeaponPools.Pool_Weapons_SMGs_04_Gemstone")
        case "Gemstone SniperRifle":
            return create_modified_item_pool(base_pool="GD_Aster_ItemPools.WeaponPools.Pool_Weapons_Snipers_04_Gemstone")
        case "Gemstone AssaultRifle":
            return create_modified_item_pool(base_pool="GD_Aster_ItemPools.WeaponPools.Pool_Weapons_ARs_04_Gemstone")

        case "Tina ClassMod":
            player_class = get_pc().PlayerClass.Name
            if player_class == "CharClass_Soldier":
                return create_modified_item_pool(base_pool="GD_Aster_ItemPools.ClassModPools.Pool_ClassMod_Soldier_Aster")
            elif player_class == "CharClass_Assassin":
                return create_modified_item_pool(base_pool="GD_Aster_ItemPools.ClassModPools.Pool_ClassMod_Assassin_Aster")
            elif player_class == "CharClass_Mercenary":
                return create_modified_item_pool(base_pool="GD_Aster_ItemPools.ClassModPools.Pool_ClassMod_Merc_Aster")
            elif player_class == "CharClass_Siren":
                return create_modified_item_pool(base_pool="GD_Aster_ItemPools.ClassModPools.Pool_ClassMod_Siren_Aster")
            elif player_class == "CharClass_Mechromancer":
                return create_modified_item_pool(base_pool="GD_Aster_ItemPools.ClassModPools.Pool_ClassMod_Mechromancer_Aster")
            elif player_class == "CharClass_LilacPlayerClass":
                return create_modified_item_pool(base_pool="GD_Aster_ItemPools.ClassModPools.Pool_ClassMod_Psycho_Aster")
            else:
                return create_modified_item_pool(base_pool="GD_Aster_ItemPools.ClassModPools.Pool_ClassMod_00_Aster")

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
    # 4 direction spawn
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=100.000000, Y=0.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=-100.000000, Y=0.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=0.000000, Y=100.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
    # sbsl_obj.SpawnVelocity=unrealsdk.make_struct("Vector", X=0.000000, Y=-100.000000, Z=300.000000)
    # sbsl_obj.ApplyBehaviorToContext(pc, unrealsdk.make_struct("BehaviorKernelInfo"), None, None, None, unrealsdk.make_struct("BehaviorParameters"))
