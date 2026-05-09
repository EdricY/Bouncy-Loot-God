import unrealsdk
import unrealsdk.unreal as unreal
from unrealsdk.hooks import Type, Block

from mods_base import get_pc, ObjectFlags
from BouncyLootGod.oob import get_loc_in_front_of_player
from BouncyLootGod.state import get_globals, get_or_create_package

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
    # "GD_Orchid_Shields.A_Item_Custom.S_BladeShield",
    # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_1340",
    # "GD_Sage_Shields.A_Item_Custom.S_BucklerShield",
    # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_PotOGold",
    # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_Order",
    # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_Equitas",
    # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Explosive_DeadlyBloom",
    # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_04_LoveThumper",
]

unique_grenade_def_names = [
    # "GD_Aster_GrenadeMods.A_Item.GM_Fireball",
    # "GD_Aster_GrenadeMods.A_Item.GM_LightningBolt",
    # "GD_Aster_GrenadeMods.A_Item.GM_MagicMissileRare",
    # "GD_Aster_GrenadeMods.A_Item.GM_MagicMissile",
    # "GD_Orchid_GrenadeMods.A_Item_Custom.GM_Blade",
    # "GD_GrenadeMods.A_Item_Custom.GM_FusterCluck",
    # "GD_GrenadeMods.A_Item_Custom.GM_KissOfDeath",
    # "GD_GrenadeMods.A_Item_Custom.GM_SkyRocket",
    # "GD_GrenadeMods.A_Item_Legendary.GM_FlameSpurt",
]

unique_relic_def_names = [
    # "GD_Artifacts.A_Item_Unique.A_Afterburner",
    # "GD_Artifacts.A_Item_Unique.A_Deputy",
    # "GD_Artifacts.A_Item_Unique.A_Endowment",
    # "GD_Artifacts.A_Item_Unique.A_Opportunity",
    # "GD_Artifacts.A_Item_Unique.A_Sheriff",
    # "GD_Artifacts.A_Item_Unique.A_VaultHunter",
    # "GD_Aster_Artifacts.A_Item_Unique.A_MysteryAmulet",
    # "GD_Orchid_Artifacts.A_Item_Unique.A_Blade",
    # "GD_Artifacts.A_Item_Unique.A_Terramorphous", # this should go here instead of in it's own category
    # "GD_Anemone_Relics.A_Item.A_Elemental_Status_Rare", # winter is over
]

individual_receivables_dict = {
    #TODO
    # "12 Pounder":'GD_Orchid_BossWeapons.Launcher.RL_Torgue_3_12Pounder',
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
                # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Standard_05_Legendary",
                # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Singularity",
                # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Spike_Acid_05_Legendary",
                # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Juggernaut_05_Legendary",
                # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Booster_05_Legendary",
                # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryShock",
                # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Absorption_05_LegendaryNormal",
                # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Impact_05_Legendary",
                # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Chimera_05_Legendary",
                # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Roid_ThresherRaid",
                # "GD_ItemGrades.Shields.ItemGrade_Gear_Shield_Nova_Phoenix",
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
                    # "GD_Itempools.ClassModPools.Pool_ClassMod_06_Legendary",
                    # "GD_Itempools.ClassModPools.Pool_ClassMod_06_SlayerOfTerramorphous",
                    # # lobelia has 3 elements per character, so add it 3 times to balance
                    # "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All", 
                    # "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All",
                    # "GD_Lobelia_Itempools.ClassModPools.Pool_ClassMod_Lobelia_All",
                ],
                uniform_probability=False,
            )

        # Relic
        case "Common Oz Kit":
            return create_modified_item_pool("BLGCommonOzKit",
                base_pool="GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
                relic_rarity="Common",
            )
        case "Uncommon Oz Kit":
            return create_modified_item_pool("BLGUncommonOzKit",
                base_pool="GD_Itempools.ArtifactPools.Pool_Artifacts_01_Common",
                relic_rarity="Uncommon",
            )
        case "Rare Oz Kit":
            return create_modified_item_pool("BLGRareOzKit",
                base_pool="GD_Itempools.ArtifactPools.Pool_Artifacts_03_Rare",
                relic_rarity="Rare",
            )
        case "VeryRare Oz Kit":
            return create_modified_item_pool("BLGVeryRareOzKit",
                base_pool="GD_Itempools.ArtifactPools.Pool_Artifacts_03_Rare",
                relic_rarity="VeryRare",
            )
        # case "Legendary Oz Kit":
            # "GD_Artifacts.A_Item_Unique.A_Terramorphous", # we should just call this unique
        case "Unique Oz Kit":
            return create_modified_item_pool("BLGUniqueOzKit",
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
        case "Legendary Pistol":
            return create_modified_item_pool("BLGLegendaryPistols",
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Pistols_06_Legendary",
                pool_names=[
                    # "GD_Anemone_ItemPools.WeaponPools.Pool_Pistol_Hector_Paradise",
                    # "GD_Anemone_Weapons.A_Weapons_Legendary.Pistol_Vladof_5_Infinity_DD" # Fire Drill
                    # "GD_Anemone_Weapons.Testing_Resist_100.100_Fire",
                ]
            )
        case "Unique Pistol":
            return create_modified_item_pool("BLGUniquePistols",
                inv_bal_def_names=[
                    "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_Starter",
                    "GD_Cork_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_CyberCol"
                    # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_Fibber",
                    # "GD_Orchid_BossWeapons.Pistol.Pistol_Jakobs_ScarletsGreed",
                    # "GD_Aster_Weapons.Pistols.Pistol_Maliwan_3_GrogNozzle",
                    # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_GwensHead",
                    # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Judge",
                    # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Hyperion_3_LadyFist",
                    # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Jakobs_3_Law",
                    # "GD_Orchid_BossWeapons.Pistol.Pistol_Maliwan_3_LittleEvie",
                    # "GD_Iris_Weapons.Pistols.Pistol_Torgue_3_PocketRocket",
                    # "GD_Sage_Weapons.Pistols.Pistol_Jakobs_3_Rex",
                    # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Maliwan_3_Rubi",
                    # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Teapot",
                    # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Bandit_3_Tenderbox",
                    # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Vladof_3_Veritas",
                    # # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_Starter",
                    # "GD_Weap_Pistol.A_Weapons_Unique.Pistol_Dahl_3_Dahlminator",
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
                    'GD_Cork_Weap_Shotgun.A_Weapons_Unique.SG_Torgue_3_JackOCannon'
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
        case "Legendary SMG":
            return create_modified_item_pool(base_pool="GD_Itempools.WeaponPools.Pool_Weapons_SMG_06_Legendary")
        case "Unique SMG":
            return create_modified_item_pool("BLGUniqueSMGs",
                inv_bal_def_names=[
                    "GD_Cork_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch"
                    # "GD_Weap_SMG.A_Weapons_Unique.SMG_Bandit_3_BoneShredder",
                    # "GD_Weap_SMG.A_Weapons_Unique.SMG_Dahl_3_Lascaux",
                    # "GD_Weap_SMG.A_Weapons_Unique.SMG_Gearbox_1",
                    # "GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Bane",
                    # "GD_Weap_SMG.A_Weapons_Unique.SMG_Hyperion_3_Commerce",
                    # "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_BadTouch",
                    # "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_Chulainn",
                    # "GD_Weap_SMG.A_Weapons_Unique.SMG_Maliwan_3_GoodTouch",
                    # "GD_Sage_Weapons.SMG.SMG_Hyperion_3_YellowJacket",
                    # "GD_Orchid_BossWeapons.SMG.SMG_Dahl_3_SandHawk",
                    # "GD_Aster_Weapons.SMGs.SMG_Bandit_3_Orc",
                    # "GD_Aster_Weapons.SMGs.SMG_Maliwan_3_Crit",
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
                    # "GD_Sage_Weapons.SniperRifles.Sniper_Jakobs_3_ElephantGun",
                    # "GD_Orchid_BossWeapons.SniperRifles.Sniper_Maliwan_3_Pimpernel",
                    # "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Buffalo",
                    # "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Maliwan_3_ChereAmie",
                    # "GD_Iris_Weapons.SniperRifles.Sniper_Jakobs_3_Cobra",
                    # "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_FremingtonsEdge",
                    # "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Hyperion_3_Morningstar",
                    # "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Dahl_3_Sloth",
                    # "GD_Weap_SniperRifles.A_Weapons_Unique.Sniper_Jakobs_3_Tresspasser",
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
        case "Legendary AssaultRifle":
            return create_modified_item_pool(
                "BLGLegendaryARs",
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_AssaultRifles_06_Legendary",
                inv_bal_def_names=[
                    # "GD_Aster_Weapons.AssaultRifles.AR_Bandit_3_Ogre",
                    # "GD_Anemone_Weapons.AssaultRifle.Brothers.AR_Jakobs_5_Brothers",
                ]
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
                    'GD_Cork_Weap_Lasers.A_Weapons_Unique.Laser_Maliwan_4_Egun'
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
        case "Legendary RocketLauncher":
            return create_modified_item_pool("BLGLegendaryRPGs",
                base_pool="GD_Itempools.WeaponPools.Pool_Weapons_Launchers_06_Legendary",
                inv_bal_def_names=[
                    "GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_Alien_Norfleet"
                ]
            )
        case "Unique RocketLauncher":
            return create_modified_item_pool("BLGUniqueRPGs",
                inv_bal_def_names=[
                    # "GD_Weap_Launchers.A_Weapons_Unique.RL_Bandit_3_Roaster",
                    # "GD_Weap_Launchers.A_Weapons_Unique.RL_Maliwan_3_TheHive",
                    # "GD_Weap_Launchers.A_Weapons_Unique.RL_Torgue_3_Creamer",
                    # "GD_Orchid_BossWeapons.Launcher.RL_Torgue_3_12Pounder",
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